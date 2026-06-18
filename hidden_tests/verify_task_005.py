import sys
import os
import math


def run_validation():
    sys.path.insert(0, os.path.abspath("./tmp_eval_workspace"))

    try:
        from bot.klippy import Klippy

        # Bypass the complex __init__ (requires ConfigWrapper + logging.Handler).
        klippy = Klippy.__new__(Klippy)

        # accel_x, accel_y, accel_z must be tracked in _SENSOR_PARAMS
        assert "accel_x" in klippy._SENSOR_PARAMS, \
            "'accel_x' not found in _SENSOR_PARAMS"
        assert "accel_y" in klippy._SENSOR_PARAMS, \
            "'accel_y' not found in _SENSOR_PARAMS"
        assert "accel_z" in klippy._SENSOR_PARAMS, \
            "'accel_z' not found in _SENSOR_PARAMS"

        # Test accelerometer message with still motion (low magnitude deviation from gravity)
        still_sensor = {
            "temperature": 25.0,
            "accel_x": 0.02,
            "accel_y": 0.01,
            "accel_z": 9.81
        }
        message_still = klippy._sensor_message("adxl345", still_sensor)
        # Should show magnitude ~9.81 m/s²
        assert "Adxl345:" in message_still, \
            f"Expected 'Adxl345:' with colon in message, got: {message_still}"
        assert any(x in message_still for x in ["9.81 m/s²", "9.8 m/s²"]), \
            f"Expected magnitude ~9.81 m/s² in message, got: {message_still}"

        # Test accelerometer message with movement (medium magnitude deviation)
        movement_sensor = {
            "temperature": 25.0,
            "accel_x": 1.5,
            "accel_y": 2.0,
            "accel_z": 10.0
        }
        message_movement = klippy._sensor_message("lis2dw12", movement_sensor)
        # Magnitude = sqrt(1.5² + 2.0² + 10.0²) ≈ 10.31 m/s²
        assert "Lis2dw12:" in message_movement, \
            f"Expected 'Lis2dw12:' with colon in message, got: {message_movement}"
        assert any(x in message_movement for x in ["10.31 m/s²", "10.3 m/s²"]), \
            f"Expected magnitude ~10.31 m/s² in message, got: {message_movement}"

        # Test accelerometer message with shaking (high magnitude deviation)
        shaking_sensor = {
            "temperature": 25.0,
            "accel_x": 3.5,
            "accel_y": 3.0,
            "accel_z": 11.5
        }
        message_shaking = klippy._sensor_message("accelerometer", shaking_sensor)
        assert "Accelerometer:" in message_shaking, \
            f"Expected 'Accelerometer:' with colon in message, got: {message_shaking}"
        assert any(x in message_shaking for x in ["12.39 m/s²", "12.4 m/s²"]), \
            f"Expected magnitude ~12.39 m/s² in message, got: {message_shaking}"

        # Test that acceleration magnitude is displayed (with proper units, no motion labels)
        assert "m/s²" in message_still or "m/s2" in message_still, \
            f"Expected acceleration magnitude with units in message, got: {message_still}"
        assert "still" not in message_still and "moving" not in message_still and "shaking" not in message_still, \
            f"Should not contain motion state labels, got: {message_still}"

        # Test sensor name formatting for various styles
        adxl_msg = Klippy._sensor_message("adxl345", still_sensor)
        assert "Adxl345:" in adxl_msg, \
            f"Expected 'Adxl345:' for input 'adxl345', got: {adxl_msg}"
        lis_msg = Klippy._sensor_message("lis2dw12", still_sensor)
        assert "Lis2dw12:" in lis_msg, \
            f"Expected 'Lis2dw12:' for input 'lis2dw12', got: {lis_msg}"
        accel_msg = Klippy._sensor_message("accelerometer", still_sensor)
        assert "Accelerometer:" in accel_msg, \
            f"Expected 'Accelerometer:' for input 'accelerometer', got: {accel_msg}"

        print("SUCCESS: Accelerometer validation passed.")
        sys.exit(0)

    except AssertionError as e:
        print(f"FAILURE: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    run_validation()
