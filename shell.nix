{ pkgs ? import <nixpkgs> {} }:
pkgs.mkShell {
  packages = with pkgs; [
    pre-commit

    tree

    nixd
    poetry
    ruff
    pyright

    caddy
    postgresql_17
    adminer
    (writeShellApplication {
      name = "adminer-serve";
      text = ''
        #!/bin/sh
        cd ${adminer} || exit 1
        nix-shell -p php --command 'php -S localhost:9001'
      '';
    })
  ];

  shellHook = ''
    source $(poetry env info --path)/bin/activate
  '';
}
