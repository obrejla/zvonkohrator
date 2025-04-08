# ZVONKOHRATOR

## How to run

### As a systemd service (e.g. autorun on startup)

1. as a root copy `zvonkohrator.service-tmp` to `/lib/systemd/system/` with the name `zvonkohrator.service` (i.e. without `-tmp` suffix)
2. replace `{PATH_TO_ZVONKOHRATOR}` in the `zvonkohrator.service` file by the real path to your local zvonkohrator repository
3. change the access rights of the `zvonkohrator.service` file to `644`, e.g. by using `sudo chmod 644 /lib/systemd/system/zvonkohrator.service`
4. reload systemd service configurations by `sudo systemctl daemon-reload`
5. run `zvonkohrator.service` using `sudo systemctl start zvonkohrator.service`

- On next system startup, service should be started automatically.

### Manually from sources

1. go to zvonkohrator project directory
2. run `source ./venv/bin/activate` to activate python virtual environment
3. run `python ./zvonkohrator_pi_5/__main__.py`

### Tests

Just run `pytest` command in the root directory.

Tests are also automatically triggered when creating Pull Request on GitHub.

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

## System related packages

**Search for lib package**

`sudo apt-cache search {LIB_NAME}`

**Packages which had to be installed**

`sudo apt-get install dbus`

`sudo apt-get install libdbus-1-3 libdbus-1-dev`

`sudo apt-get install libglib2.0-dev`

## Game modes

### Keyboard

In this mode, **ZVONKOHRATOR** works with the attached MIDI keyboard and allows the user to play pressed tones. There is also a possibility to record a tone sequence for each of 4 teams.

When the mode is activated, MIDI keyboard must be attached, otherwise the error is shown on the LCD. Then when the MIDI keyboard is attached, mode must be activated by its button again.

This mode has 5 *sub modes*. Currently selected *sub mode* is indicated by numbers in the top right corner of the LCD, like `1/5`.

When the mode is started, then first *sub mode* is just a *play tones* mode. User can press MIDI keyboard keys and proper tones are direcly played by **ZVONKOHRATOR**.

When a team wants to record their tone sequence (like if they have some sort of simple *team anthem*), they can use **PREV** or **NEXT** buttons of the player controller to move to sub mode of their team (indicated by the team name in the bottom left corner of the LCD). Once they are there, they can record their tone sequence. Recording is triggered by *pressing-and-holding* **STOP** button. When recording starts, the text `RECING!` is displayed on the LCD. Now the team can *play* their tones. Once they are done, they just simply press **STOP** button and their sequence is stored directly to the device. They can play it just by pressing **PLAY/PAUSE** button when their *team sub mode* is selected.

When the recording is started and stopped without any tone pressed, the recorded tone sequence is deleted.

### Cassette

In this mode, **ZVONKOHRATOR** expects *cassette* to be inserted inside a cassette slot. Cassettes are designed in a way that after the insert, they push 1-4 buttons creating a bitmask of the number 1-15. It means, that there can exist 15 cassettes for 15 songs. Those songs are MIDI files stored in the local storage inside `cassette-files` directory. Those files must be prefixed with a number and dash, e.g. `13-some-song.mid`.

There is no need to have *all 15* song files there. When cassette is inserted and there is no corresponding song file found, it is displayed on the LCD.

Once the cassette is inserted and song loaded, it can be operated by those player controls:

- **STOP** - stops currently playing cassette song file
- **PLAY/PAUSE** - starts the currently loaded cassette file, if it is not playing, or pause the currently playing file

### Files

In this mode **ZVONKOHRATOR** acts as a player for the MIDI files. Those can be stored directly on the device in `midi-files` folder or in attached USB drive (those must be at root of the USB drive). All files are loaded on game mode start.

Controls for the player are:

- **PREV** - go to previous loaded file, works only when the file is not playing or paused
- **STOP** - stops currently playing file
- **PLAY/PAUSE** - starts the currently selected file, if it is not playing, or pause the currently playing file
- **NEXT** - go to next loaded file, works only when the file is not playing or paused

### Teams

It is actually just extended *Files* mode. It can play MIDI files from the local storage from `midi-files` directory, or from attached USD drive.

But it is extended by the possibility to *Pause* the playing by the special *Team* buttons. Those are 4 colored buttons - when the team presses their button, it:

1) lights up
2) pauses the playing of the current file
3) shows the team name on the LCD display

All teams can press/pause even in case when the file is already paused. They are displayed in the correct order on the LCD.

Opeartor can then stop the song or un-pause it, in such a case the team button lights are turned off.

## General functionality

### Energy flow

Entire **ZVONKOHRATOR** works only in case when the *energy is flowing*. It is implemented the way like when the *energy button* is pressed. If it is not pressed, it is reported to LCD and nothing works. Once the energy *starts flowing*, **ZVONKOHRATOR** starts working as expected. *Pressing* the button is implemented by sending the signal to expected raspi pin, e.g. from *energy generating bike dynamo* and related electronic components.

### Shutdown button

There is a shutdown button to gracefully shut down raspi before the energy is turned off. Button must be pressed for few seconds, the it is displayed on the LCD that shutdown is in progress - with a loading bar.

When the loading bar is in progress, another press of the shutdown button cancels the shutdown process and sets **ZVONKOHRATOR** to its initial state.

### Remote control

It is posible to control *player* (i.e. Prev, Stop, Play/Pause and Next buttons) remotely via bluetooth - using **Android** phone with installed [Blue Dot](https://play.google.com/store/apps/details?id=com.stuffaboutcode.bluedot) app. There is also available [documentaion for the Blue Dot](https://bluedot.readthedocs.io/en/latest/pairpiandroid.html) itself.

You need to pair the phone with the Raspberry, so:
1. log in to Raspberry,
2. in the top right corner click on Bluetooth icon,
3. and click *Make Discoverable*
4. Then on the phone try to find the Raspberry device and proceed with pairing.
5. Once the device is paired, you can run **Blue Dot** app on your phone and you should see the Raspberry device in the list.
6. Tap on the device and it shoud *connect*.
7. Then 4 color circles should appear on the Phone screen (without any labels).

- There should be *2 yellow* circles - the one on the left should be for **PREV** action and the one on the right should be for **NEXT** action.
- There should be one *red* circle - it should trigger **STOP** action.
- And the last one is *green* circle - it should trigger **PLAY/PAUSE** action.

Remote controls can be used whenever common *player* buttons can be used.

## License

[MIT](LICENSE.txt)
