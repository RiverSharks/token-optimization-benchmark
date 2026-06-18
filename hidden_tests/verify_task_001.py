import sys
import os


def run_validation():
    sys.path.insert(0, os.path.abspath("./tmp_eval_workspace"))

    try:
        from bot.klippy import Klippy

        # Bypass the complex __init__ (requires ConfigWrapper + logging.Handler).
        # _SENSOR_PARAMS is a class attribute; the new methods under test
        # (_format_sensor_name, get_sensors_string) only need class-level state.
        klippy = Klippy.__new__(Klippy)

        # humidity must be tracked in _SENSOR_PARAMS
        assert "humidity" in klippy._SENSOR_PARAMS, \
            "'humidity' not found in _SENSOR_PARAMS"

        # Test exact output from commit: "🌡️ Sht3X: 25 °C 💧 45%"
        sensor_value = {"temperature": 24.7, "humidity": 45.3}
        message = klippy._sensor_message("sht3x", sensor_value)
        # Check that humidity is present with droplet emoji
        assert "💧" in message and "45" in message, \
            f"Expected humidity with droplet emoji, got: {message}"
        # Check that sensor name is properly formatted (Sht3X)
        assert "Sht3X" in message, \
            f"Expected 'Sht3X' in message, got: {message}"
        # Check temperature is displayed
        assert "25" in message and "°C" in message, \
            f"Expected temperature display, got: {message}"

        # Test sensor name formatting for various input styles
        temp_only = {"temperature": 20.0}
        assert "Sht3X:" in Klippy._sensor_message("sht3x", temp_only), \
            "Expected 'Sht3X:' for input 'sht3x'"
        assert "Sht3X:" in Klippy._sensor_message("SHT3X", temp_only), \
            "Expected 'Sht3X:' for input 'SHT3X'"
        assert "Bme280:" in Klippy._sensor_message("bme280", temp_only), \
            "Expected 'Bme280:' for input 'bme280'"
        assert "Heater Bed:" in Klippy._sensor_message("heater_bed", temp_only), \
            "Expected 'Heater Bed:' for input 'heater_bed'"
        assert "Heater Bed:" in Klippy._sensor_message("heaterBed", temp_only), \
            "Expected 'Heater Bed:' for input 'heaterBed'"
        assert "Extruder:" in Klippy._sensor_message("extruder", temp_only), \
            "Expected 'Extruder:' for input 'extruder'"

        print("SUCCESS: Deterministic validation passed.")
        sys.exit(0)

    except Exception as e:
        print(f"FAILURE: Code validation failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_validation()
