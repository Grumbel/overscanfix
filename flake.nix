{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        pythonPackages = pkgs.python3Packages;

        PyQt5-stubs = pythonPackages.buildPythonPackage rec {
          pname = "PyQt5-stubs";
          version = "5.15.6.0";
          src = pythonPackages.fetchPypi {
            inherit pname version;
            sha256 = "sha256-kScKwj6/OKHcBM2XqoUs0Ir4Lcg5EA5Tla8UR+Pplwc=";
          };
        };
      in rec {
        packages = rec {
          default = overscanfix;

          overscanfix = pythonPackages.buildPythonPackage rec {
            pname = "overscanfix";
            version = "0.0.0";

            src = ./.;

            doCheck = false;

            makeWrapperArgs = [
              "\${qtWrapperArgs[@]}"
            ];

            preCheck = ''
              export QT_QPA_PLATFORM_PLUGIN_PATH="${pkgs.qt5.qtbase.bin}/lib/qt-${pkgs.qt5.qtbase.version}/plugins";
            '';

            checkPhase = ''
              runHook preCheck
              flake8
              mypy -p overscanfix  # -p tests
              pylint overscanfix  # tests
              # python3 -m unittest discover -v -s tests/
              runHook postCheck
            '';

            nativeBuildInputs = [
              pkgs.qt5.wrapQtAppsHook
            ];

            nativeCheckInputs = [
              PyQt5-stubs
              pythonPackages.flake8
              pythonPackages.mypy
              pythonPackages.pylint
              pythonPackages.types-setuptools
              pythonPackages.pip
            ];

            propagatedBuildInputs = [
              pythonPackages.pyqt5
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
