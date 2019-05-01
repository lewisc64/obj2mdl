# obj2mdl

Converts a `.obj` file to a source `.mdl`. It will create intermediary `.smd` files, for `studiomdl.exe` to use.

## Usage

Run the file and follow the directions, or use the command line:
 - `obj2mdl.py model.json`

Run `obj2mdl.py -help` for more information.

## Configuration

### Program

The `config.json` file should look like this:
```json
{
  "engine_path": "PATH_TO_BIN_FOLDER",
  "game_path": "PATH_TO_GAME_FOLDER"
}
```

 - `engine_path` is the folder that contains `studiomdl.exe`.
 - `game_path` is the folder of the game, for example something like: `C:\Program Files (x86)\Steam\SteamApps\common\Half-Life 2\hl2`.

### Model Config

To get the auto-generated collision model, simply set `obj_collision_model` to the value of `obj`. If `material -> use_file` is true, then the materials specified in the OBJ file will be used. Otherwise, every face will recieve the material name given by `material -> name`.

The contents of `MODEL_NAME.json` should look like this:

```json
{
  
  "name": "sofa",
  
  "obj": "sofa.obj",
  "obj_collision_model": "sofa_collision.obj",

  "material": {
    "use_file": false,
    "name": "sofa"
  },
  
  "qc": {
	"surfaceprop": "wood",
  }
  
}
```

All attributes of `qc` correspond to the output of the qc. If a property isn't specified, a set default is used. Alternatively, you can provide your own QC file:

```json
{
  
  "name": "sofa",
  
  "obj": "sofa.obj",
  "obj_collision_model": "sofa_collision.obj",

  "material": {
    "use_file": false,
    "name": "sofa"
  },
  
  "qc": "sofa.qc"
  
}
```
