from odoo import Command
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase


class TestConnectorProfile(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.manager_group = cls.env.ref("insitu_sales_connector.group_insitu_manager")
        cls.sales_group = cls.env.ref("sales_team.group_sale_salesman_all_leads")
        cls.stock_group = cls.env.ref("stock.group_stock_user")
        cls.contact_group = cls.env.ref("base.group_partner_manager")
        cls.env.user.write(
            {
                "groups_id": [
                    Command.link(cls.manager_group.id),
                    Command.link(cls.sales_group.id),
                    Command.link(cls.stock_group.id),
                ]
            }
        )
        cls.integration_user = cls.env["res.users"].create(
            {
                "name": "inSitu Connector Test User",
                "login": "insitu-connector-test",
                "company_id": cls.env.company.id,
                "company_ids": [Command.set([cls.env.company.id])],
                "groups_id": [
                    Command.set(
                        [
                            cls.env.ref(
                                "insitu_sales_connector.group_insitu_integration"
                            ).id,
                            cls.sales_group.id,
                            cls.stock_group.id,
                            cls.contact_group.id,
                        ]
                    )
                ],
            }
        )
        cls.profile = cls.env["insitu.connector.profile"].create(
            {
                "name": "Test Connector",
                "company_id": cls.env.company.id,
                "integration_user_id": cls.integration_user.id,
            }
        )

    def test_validate_and_health_check(self):
        result = self.profile.action_validate_setup()
        self.assertIn(
            self.profile.state,
            {"ready", "warning"},
            msg=self.profile.validation_message,
        )
        self.assertEqual(result["tag"], "display_notification")

        info = (
            self.env["insitu.connector.profile"]
            .with_user(self.integration_user)
            .get_connector_info()
        )
        self.assertTrue(info["configured"])
        self.assertEqual(info["profile_id"], self.profile.id)
        self.assertEqual(info["database"], self.env.cr.dbname)

    def test_report_sync_result(self):
        result = self.env["insitu.connector.profile"].with_user(
            self.integration_user
        ).report_sync_result(
            {
                "entity": "orders",
                "direction": "to_odoo",
                "status": "success",
                "processed_count": 3,
                "error_count": 0,
                "message": "Orders synchronized",
            }
        )
        log = self.env["insitu.sync.log"].browse(result["log_id"])
        self.assertEqual(log.processed_count, 3)
        self.assertEqual(log.profile_id, self.profile)
        self.assertEqual(self.profile.last_sync_status, "success")

    def test_reject_invalid_sync_payload(self):
        with self.assertRaises(ValidationError):
            self.env["insitu.connector.profile"].report_sync_result(
                {
                    "entity": "unknown",
                    "direction": "to_odoo",
                    "status": "success",
                }
            )

    def test_integration_user_marks_created_records(self):
        partner = self.env["res.partner"].with_user(self.integration_user).create(
            {"name": "Connector Customer"}
        )
        self.assertTrue(partner.insitu_origin)
        self.assertEqual(partner.insitu_sync_status, "success")
        self.assertTrue(partner.insitu_last_sync_at)

    def test_connector_manager_is_not_marked_as_integration_origin(self):
        partner = self.env["res.partner"].create({"name": "Manual Customer"})
        self.assertFalse(partner.insitu_origin)
        self.assertFalse(partner.insitu_last_sync_at)

    def test_service_user_cannot_bypass_sync_result_validation(self):
        with self.assertRaises(AccessError):
            self.env["insitu.sync.log"].with_user(self.integration_user).create(
                {
                    "profile_id": self.profile.id,
                    "company_id": self.env.company.id,
                    "entity": "orders",
                    "direction": "to_odoo",
                    "status": "success",
                }
            )
