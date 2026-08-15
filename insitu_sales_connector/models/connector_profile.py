from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, ValidationError


class InsituConnectorProfile(models.Model):
    _name = "insitu.connector.profile"
    _description = "inSitu Sales Connector Profile"
    _order = "company_id, id"

    name = fields.Char(required=True, default="inSitu Sales")
    active = fields.Boolean(default=True)
    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company,
        index=True,
        ondelete="cascade",
    )
    tenant_reference = fields.Char(
        string="inSitu Company Reference",
        help="Optional inSitu company or tenant identifier supplied by the integration team.",
    )
    integration_user_id = fields.Many2one(
        "res.users",
        string="Odoo Integration User",
        domain="[('share', '=', False), ('active', '=', True)]",
        help=(
            "Use a dedicated internal Odoo user. Generate its API key in Odoo "
            "and share it only through an approved secret channel."
        ),
    )
    state = fields.Selection(
        [
            ("draft", "Needs Setup"),
            ("ready", "Ready"),
            ("warning", "Ready with Warnings"),
            ("error", "Configuration Error"),
        ],
        required=True,
        default="draft",
        copy=False,
        index=True,
    )
    validation_message = fields.Text(readonly=True, copy=False)
    last_validated_at = fields.Datetime(readonly=True, copy=False)
    last_sync_at = fields.Datetime(readonly=True, copy=False, index=True)
    last_sync_status = fields.Selection(
        [
            ("success", "Successful"),
            ("warning", "Warning"),
            ("failed", "Failed"),
        ],
        readonly=True,
        copy=False,
        index=True,
    )
    last_sync_message = fields.Text(readonly=True, copy=False)
    log_retention_days = fields.Integer(
        default=90,
        required=True,
        help=(
            "Successful synchronization logs older than this many days are removed "
            "automatically. Warning and failed logs are retained."
        ),
    )
    odoo_url = fields.Char(compute="_compute_connection_details", string="Odoo URL")
    database_name = fields.Char(compute="_compute_connection_details")
    integration_login = fields.Char(compute="_compute_connection_details")

    @api.depends("integration_user_id", "integration_user_id.login")
    def _compute_connection_details(self):
        base_url = self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")
        database_name = self.env.cr.dbname
        for profile in self:
            profile.odoo_url = base_url
            profile.database_name = database_name
            profile.integration_login = profile.integration_user_id.login or ""

    @api.constrains("company_id")
    def _check_one_profile_per_company(self):
        for profile in self:
            duplicate_count = self.search_count(
                [("company_id", "=", profile.company_id.id), ("id", "!=", profile.id)]
            )
            if duplicate_count:
                raise ValidationError(
                    _("Only one inSitu Sales connector profile is allowed per Odoo company.")
                )

    @api.constrains("log_retention_days")
    def _check_log_retention_days(self):
        if any(profile.log_retention_days < 7 for profile in self):
            raise ValidationError(_("Log retention must be at least 7 days."))

    @api.constrains("integration_user_id", "company_id")
    def _check_integration_user_company(self):
        for profile in self.filtered("integration_user_id"):
            if profile.company_id not in profile.integration_user_id.company_ids:
                raise ValidationError(
                    _("The integration user must have access to the profile's Odoo company.")
                )

    def action_validate_setup(self):
        self.ensure_one()
        errors = []
        warnings = []
        user = self.integration_user_id
        if not user:
            errors.append(_("Select a dedicated Odoo integration user."))
        elif not user.active or user.share:
            errors.append(_("The integration user must be an active internal user."))
        else:
            if not user.has_group("insitu_sales_connector.group_insitu_integration"):
                errors.append(_("Assign the inSitu Sales / Integration Service role."))
            if not user.has_group("sales_team.group_sale_salesman_all_leads"):
                warnings.append(_("Grant sales access if orders and customers will synchronize."))
            if not user.has_group("base.group_partner_manager"):
                warnings.append(
                    _("Grant contact creation access if customers will synchronize to Odoo.")
                )
            if not user.has_group("stock.group_stock_user"):
                warnings.append(_("Grant inventory access if stock will synchronize."))
            if not user.has_group("account.group_account_invoice"):
                warnings.append(
                    _("Grant invoicing access if invoices or payments will synchronize.")
                )

        if not self.odoo_url.startswith("https://"):
            warnings.append(_("Use an HTTPS Odoo base URL before enabling production sync."))
        if not self.env["res.partner"].search_count(
            [("company_id", "in", [False, self.company_id.id])], limit=1
        ):
            warnings.append(_("No customers are currently available to synchronize."))
        if not self.env["product.product"].search_count([], limit=1):
            warnings.append(_("No products are currently available to synchronize."))

        if errors:
            state = "error"
            notification_type = "danger"
            message = "\n".join(errors + warnings)
            title = _("Setup is incomplete")
        elif warnings:
            state = "warning"
            notification_type = "warning"
            message = "\n".join(warnings)
            title = _("Setup is usable with warnings")
        else:
            state = "ready"
            notification_type = "success"
            message = _("The Odoo-side connector setup is ready.")
            title = _("Connector ready")

        self.write(
            {
                "state": state,
                "validation_message": message,
                "last_validated_at": fields.Datetime.now(),
            }
        )
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": title,
                "message": message,
                "type": notification_type,
                "sticky": bool(errors),
            },
        }

    def action_open_sync_logs(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "insitu_sales_connector.action_insitu_sync_log"
        )
        action["domain"] = [("profile_id", "=", self.id)]
        action["context"] = {
            "default_profile_id": self.id,
            "default_company_id": self.company_id.id,
        }
        return action

    @api.model
    def get_connector_info(self):
        """Return non-secret Odoo connection and readiness data over RPC."""
        self._require_connector_role()
        profile = self.search([("company_id", "=", self.env.company.id)], limit=1)
        if not profile:
            return {"configured": False, "company_id": self.env.company.id}
        self._check_assigned_user(profile)
        module = self.env["ir.module.module"].sudo().search(
            [("name", "=", "insitu_sales_connector")], limit=1
        )
        return {
            "configured": True,
            "profile_id": profile.id,
            "company_id": profile.company_id.id,
            "tenant_reference": profile.tenant_reference or None,
            "state": profile.state,
            "odoo_url": profile.odoo_url,
            "database": profile.database_name,
            "login": profile.integration_login,
            "last_sync_at": fields.Datetime.to_string(profile.last_sync_at)
            if profile.last_sync_at
            else None,
            "last_sync_status": profile.last_sync_status or None,
            "module_version": module.latest_version or None,
        }

    @api.model
    def report_sync_result(self, payload):
        """Persist a synchronization summary sent by the inSitu service."""
        self._require_connector_role()
        if not isinstance(payload, dict):
            raise ValidationError(_("The synchronization payload must be an object."))

        entity = str(payload.get("entity", "")).strip().lower()
        direction = str(payload.get("direction", "")).strip().lower()
        status = str(payload.get("status", "")).strip().lower()
        allowed_entities = {
            "customers",
            "products",
            "inventory",
            "orders",
            "invoices",
            "payments",
            "pricing",
            "warehouses",
            "estimates",
            "taxes",
            "sales_terms",
            "sales_reps",
            "payment_methods",
            "full",
        }
        if entity not in allowed_entities:
            raise ValidationError(_("Unsupported synchronization entity: %s", entity))
        if direction not in {"to_odoo", "from_odoo", "bidirectional"}:
            raise ValidationError(_("Unsupported synchronization direction: %s", direction))
        if status not in {"success", "warning", "failed"}:
            raise ValidationError(_("Unsupported synchronization status: %s", status))

        profile = self.search([("company_id", "=", self.env.company.id)], limit=1)
        if not profile:
            raise ValidationError(_("Configure the inSitu Sales connector for this company first."))
        self._check_assigned_user(profile)

        processed_count = self._safe_nonnegative_integer(payload.get("processed_count", 0))
        error_count = self._safe_nonnegative_integer(payload.get("error_count", 0))
        message = str(payload.get("message") or "")[:2000]
        started_at = self._safe_datetime(payload.get("started_at"))
        finished_at = self._safe_datetime(payload.get("finished_at")) or fields.Datetime.now()

        log = self.env["insitu.sync.log"].sudo().create(
            {
                "profile_id": profile.id,
                "company_id": profile.company_id.id,
                "entity": entity,
                "direction": direction,
                "status": status,
                "processed_count": processed_count,
                "error_count": error_count,
                "message": message,
                "started_at": started_at,
                "finished_at": finished_at,
            }
        )
        profile.sudo().write(
            {
                "last_sync_at": finished_at,
                "last_sync_status": status,
                "last_sync_message": message,
            }
        )
        return {"accepted": True, "log_id": log.id, "profile_id": profile.id}

    @api.model
    def _require_connector_role(self):
        if not self.env.user.has_group("insitu_sales_connector.group_insitu_integration"):
            raise AccessError(_("The inSitu Sales Integration Service role is required."))

    @api.model
    def _check_assigned_user(self, profile):
        if (
            profile.integration_user_id
            and self.env.user != profile.integration_user_id
            and not self.env.user.has_group("insitu_sales_connector.group_insitu_manager")
        ):
            raise AccessError(_("This user is not assigned to the active connector profile."))

    @api.model
    def _safe_nonnegative_integer(self, value):
        try:
            result = int(value or 0)
        except (AssertionError, TypeError, ValueError) as exc:
            raise ValidationError(_("Synchronization counts must be integers.")) from exc
        if result < 0:
            raise ValidationError(_("Synchronization counts cannot be negative."))
        return result

    @api.model
    def _safe_datetime(self, value):
        if not value:
            return False
        try:
            return fields.Datetime.to_datetime(value)
        except (AssertionError, TypeError, ValueError) as exc:
            raise ValidationError(_("Invalid synchronization date: %s", value)) from exc

    @api.model
    def _cron_purge_logs(self):
        now = fields.Datetime.now()
        for profile in self.search([("active", "=", True)]):
            cutoff = now - timedelta(days=profile.log_retention_days)
            logs = self.env["insitu.sync.log"].search(
                [
                    ("profile_id", "=", profile.id),
                    ("status", "=", "success"),
                    ("finished_at", "<", cutoff),
                ],
                limit=10000,
            )
            logs.unlink()
