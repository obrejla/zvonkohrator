# ZVONKOHRATOR

## How to run

### As a systemd service (e.g. autorun on startup)

1. as a root copy `zvonkohrator.service-tmp` to `/lib/systemd/system/` with the name `zvonkohrator.service` (i.e. without `-tmp` suffix)
2. change the access rights of the `zvonkohrator.service` file to `644`, e.g. by using `/lib/systemd/system/zvonkohrator.service`
3. reload systemd service configurations by `sudo systemctl daemon-reload`
4. run `zvonkohrator.service` using `sudo systemctl start zvonkohrator.service`

- On next system startup, service should be started automatically.

### Manually from sources

1. go to zvonkohrator project directory
2. run `source ./venv/bin/activate` to activate python virtual environment
3. run `python ./zvonkohrator-pi-5/__main__.py`


## Useful commands

**To start service manually**

`sudo systemctl start zvonkohrator.service`

**To stop service manually**

`sudo systemctl stop zvonkohrator.service`

**To see the status of the service**

`sudo systemctl status zvonkohrator.service`

**To reload systemd services configurations**

`sudo systemctl daemon-reload`

**To see logs from the service**

`journalctl -u zvonkohrator.service -e`
