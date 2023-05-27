{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";

    PyQt6-stubs_src.url = "github:python-qt-tools/PyQt6-stubs";
    PyQt6-stubs_src.flake = false;
  };

  outputs = { self, nixpkgs, flake-utils, PyQt6-stubs_src }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python3Packages;

        PyQt6-stubs = pythonPackages.buildPythonPackage rec {
          name = "PyQt5-stubs";
          src = PyQt6-stubs_src;

          nativeCheckInputs = with pythonPackages; [
            libcst
            mypy
            pyqt6
          ];
        };
      in rec {
        packages = rec {
          default = overscanfix;

          overscanfix = pythonPackages.buildPythonPackage rec {
            pname = "overscanfix";
            version = "0.0.0";

            src = ./.;

            doCheck = true;

            makeWrapperArgs = [
              "\${qtWrapperArgs[@]}"
            ];

            checkPhase = ''
              runHook preCheck
              flake8
              mypy -p overscanfix  # -p tests
              pylint --extension-pkg-whitelist=PyQt6 overscanfix  # tests
              # python3 -m unittest discover -v -s tests/
              runHook postCheck
            '';

            nativeBuildInputs = with pkgs; [
              qt6.wrapQtAppsHook
            ];

            buildInputs = with pkgs; [
              qt6.qtbase
            ];

            nativeCheckInputs = with pythonPackages; [
              flake8
              mypy
              pylint
              types-setuptools
              pip
            ] ++ [
              PyQt6-stubs
            ];

            propagatedBuildInputs = with pythonPackages; [
              pyqt6
            ];
          };
        };
      }
    );
}
