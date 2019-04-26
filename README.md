# obj2mdl

Converts a `.obj` file to a source `.mdl`. It will create an intermediary `.smd` file, for `studiomdl.exe` to use.

## Usage

Run the file and follow the directions, or use the command line:
 - `obj2mdl.py model.obj`

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

### Model

Each `MODEL_NAME.obj` should have a `MODEL_NAME.json` in the same folder. The contents should look like this:

```json
{
  
  "name": "sofa",

  "material": {
    "use_file": false,
    "name": "sofa"
  },
  
  "auto_generate_qc": true,
  "qc": {
	"surfaceprop": "wood",
	"collisionmodel": {
	  "automass": true
	}
  }
  
}
```

Alternatively, you can provide your own QC file. Just ensure that it is in the same directory as the model.

```json
{
  
  "name": "sofa",

  "material": {
    "use_file": false,
    "name": "sofa"
  },
  
  "auto_generate_qc": false,
  
}
```

If `material -> use_file` is true, then the materials specified in the OBJ file will be used. Otherwise, every face will recieve the material name given by `material -> name`.
