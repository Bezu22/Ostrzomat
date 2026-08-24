import unittest
from unittest.mock import patch

from logic import cart_logic


class BooleanValue:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class TestCartLogic(unittest.TestCase):
    def test_tool_price_returns_total_for_valid_decimal_input(self):
        with patch("logic.cart_logic.database.get_tool_price", return_value=100.0) as get_price:
            unit, total = cart_logic.calculate_tool_price("Frez", "4", "10,5", "5")

        self.assertEqual((unit, total), (100.0, 500.0))
        get_price.assert_called_once_with("Frez", "4", 10.5, 5)

    def test_tool_price_clamps_heavy_wear_quantity_to_order_quantity(self):
        with patch("logic.cart_logic.database.get_tool_price", return_value=100.0):
            unit, total = cart_logic.calculate_tool_price(
                "Frez", "4", "10", "4", heavy_wear_qty="99"
            )

        self.assertEqual((unit, total), (105.0, 420.0))

    def test_tool_price_rejects_invalid_and_non_positive_inputs(self):
        invalid_inputs = [("abc", "1"), ("10", "0"), ("10", "-2"), ("0", "2"), ("10", "2.5")]
        with patch("logic.cart_logic.database.get_tool_price") as get_price:
            for diam, qty in invalid_inputs:
                self.assertEqual(
                    cart_logic.calculate_tool_price("Frez", "4", diam, qty),
                    (0.0, 0.0),
                )

        get_price.assert_not_called()

    def test_extra_services_ignore_disabled_items_and_cap_quantities(self):
        services = {
            "ciecie": BooleanValue(True),
            "opuszczenie": BooleanValue(True),
            "polerowanie": BooleanValue(False),
            "zuzycie": BooleanValue(True),
        }
        quantities = {"ciecie": "99", "opuszczenie": "-2"}
        with patch("logic.cart_logic.database.get_service_price_refined", return_value=10.0):
            unit, total, labels = cart_logic.calculate_extra_services(
                services, quantities, "8", 3, opuszczenie_multiplier=2
            )

        self.assertEqual((unit, total), (10.0, 30.0))
        self.assertEqual(labels, ["Cięcie", "Zaniżenie średnicy"])

    def test_extra_services_bad_quantity_does_not_crash_preview(self):
        services = {"ciecie": BooleanValue(True)}
        with patch("logic.cart_logic.database.get_service_price_refined", return_value=12.5):
            result = cart_logic.calculate_extra_services(services, {"ciecie": "xyz"}, "8", 2)

        self.assertEqual(result, (0.0, 0.0, ["Cięcie"]))

    def test_extra_services_rejects_zero_negative_and_invalid_totals(self):
        services = {"ciecie": BooleanValue(True)}
        for diam, quantity in [("8", 0), ("8", -1), ("bad", 2)]:
            self.assertEqual(
                cart_logic.calculate_extra_services(services, {}, diam, quantity),
                (0.0, 0.0, []),
            )

    def test_service_breakdown_returns_each_component(self):
        statuses = {"ciecie": True, "opuszczenie": True, "polerowanie": True}
        quantities = {"ciecie": "2", "opuszczenie": "99", "polerowanie": "1"}

        def service_price(name, _diam):
            return {"Cięcie": 4.0, "Zaniżenie średnicy": 5.0, "Polerowanie rowka": 6.0}[name]

        with patch("logic.cart_logic.database.get_service_price_refined", side_effect=service_price):
            breakdown = cart_logic.calculate_service_breakdown(statuses, quantities, "8", 3, 2)

        self.assertEqual(breakdown, {"ciecie": 8.0, "opuszczenie": 30.0, "polerowanie": 6.0})

    def test_coating_price_handles_decimal_inputs_and_invalid_values(self):
        with patch("logic.cart_logic.database.get_coating_price", return_value=25.555):
            self.assertEqual(
                cart_logic.calculate_coating_price("TiN", "10,5", "20", "2"),
                (25.555, 51.11),
            )

        with patch("logic.cart_logic.database.get_coating_price") as get_price:
            invalid_values = [
                ("TiN", "0", "20", "1"),
                ("TiN", "10", "0", "1"),
                ("TiN", "10", "20", "0"),
                ("Brak", "10", "20", "1"),
            ]
            for values in invalid_values:
                self.assertEqual(cart_logic.calculate_coating_price(*values), (0.0, 0.0))

        get_price.assert_not_called()


if __name__ == "__main__":
    unittest.main()
