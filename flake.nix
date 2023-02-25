{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python39Packages;
      in rec {
        packages = rec {
          default = overscanfix;

          PyQt5-stubs = pythonPackages.buildPythonPackage rec {
            pname = "PyQt5-stubs";
            version = "5.15.6.0";
            src = pythonPackages.fetchPypi {
              inherit pname version;
              sha256 = "sha256-kScKwj6/OKHcBM2XqoUs0Ir4Lcg5EA5Tla8UR+Pplwc=";
            };
          };

          overscanfix = pythonPackages.buildPythonPackage rec {
            pname = "overscanfix";
            version = "0.0.0";

            src = ./.;

            preCheck = ''
              export QT_QPA_PLATFORM_PLUGIN_PATH="${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins";
            '';

            doCheck = false;

            checkPhase = ''
              runHook preCheck
              flake8
              mypy -p overscanfix  # -p tests
              pylint overscanfix  # tests
              # python3 -m unittest discover -v -s tests/
              runHook postCheck
            '';

            propagatedBuildInputs = [
              pythonPackages.pyqt5
            ];

            # nativeBuildInputs = [
            # ];

            checkInputs = [
              PyQt5-stubs
              pythonPackages.flake8
              pythonPackages.mypy
              pythonPackages.pylint
              pythonPackages.types-setuptools
              pythonPackages.pip
            ];
          };
        };

        devShells = rec {
          default = overscanfix;

          overscanfix = pkgs.mkShell {
            inputsFrom = [ packages.overscanfix ];
            shellHook = ''
              export QT_QPA_PLATFORM_PLUGIN_PATH="${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins";
              runHook setuptoolsShellHook
            '';
          };
        };
      }
    );
}
