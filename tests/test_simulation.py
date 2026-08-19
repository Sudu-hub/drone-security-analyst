from src.frame_simulator import FrameSimulator
from src.telemetry_simulator import TelemetrySimulator


def test_frames_are_loaded():
    simulator = FrameSimulator()

    frames = simulator.get_frames()

    assert len(frames) > 0
    assert "frame_id" in frames[0]
    assert "timestamp" in frames[0]
    assert "description" in frames[0]


def test_telemetry_is_loaded():
    simulator = TelemetrySimulator()

    telemetry = simulator.get_telemetry()

    assert len(telemetry) > 0
    assert "timestamp" in telemetry[0]
    assert "location" in telemetry[0]
    assert "altitude" in telemetry[0]