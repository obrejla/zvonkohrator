import threading
import time
from unittest.mock import MagicMock, patch

import pytest

from zvonkohrator_pi_5.EnergyController import Energy, EnergyController


@pytest.fixture
def energy_controller():
    with patch("zvonkohrator_pi_5.EnergyController.Button") as MockButton:
        mock_button = MagicMock()
        MockButton.return_value = mock_button
        controller = EnergyController()
        return controller, mock_button


def test_energy_on_triggers_listeners(energy_controller):
    controller, _ = energy_controller

    listener = MagicMock()
    controller.add_energy_flow_listener(listener)

    controller._EnergyController__energy_on()

    assert controller.is_energy_flowing()
    listener.assert_called_with(Energy.FLOWS)


def test_energy_off_triggers_listeners(energy_controller):
    controller, _ = energy_controller

    listener = MagicMock()
    controller.add_energy_flow_listener(listener)

    controller._EnergyController__energy_off()

    assert not controller.is_energy_flowing()
    listener.assert_called_with(Energy.NONE)


def test_init_when_energy_is_pressed(energy_controller):
    controller, mock_button = energy_controller
    mock_button.is_pressed = True

    controller.init()

    assert controller.is_energy_flowing()


def test_init_when_energy_is_not_pressed(energy_controller):
    controller, mock_button = energy_controller
    mock_button.is_pressed = False

    controller.init()

    assert not controller.is_energy_flowing()


def test_start_and_stop_bypass(energy_controller):
    controller, mock_button = energy_controller

    controller.start_bypass()
    assert controller.is_energy_flowing()

    mock_button.is_pressed = False
    controller.stop_bypass()
    assert not controller.is_energy_flowing()

    mock_button.is_pressed = True
    controller.stop_bypass()
    assert controller.is_energy_flowing()


def test_wait_for_energy_unblocks_when_energy_flows(energy_controller):
    controller, _ = energy_controller
    result = {"flowed": False}

    def waiter():
        controller.wait_for_energy()
        result["flowed"] = True

    thread = threading.Thread(target=waiter)
    thread.start()

    # wait for a while to check that Thread really blocks
    time.sleep(0.1)
    assert not result["flowed"], "wait_for_energy should be blocking"

    controller._EnergyController__energy_on()

    # wait so the Thread has a chance to wake up
    thread.join(timeout=1)
    assert result["flowed"], "wait_for_energy should continue after energy_on"


def test_wait_for_energy_does_not_block_if_already_set(energy_controller):
    controller, _ = energy_controller
    controller._EnergyController__energy_on()

    start = time.time()
    controller.wait_for_energy()
    duration = time.time() - start

    assert duration < 0.05, "wait_for_energy should NOT be blocking when energy flows"
