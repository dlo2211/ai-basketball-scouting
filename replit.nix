{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.requests
    pkgs.python311Packages.beautifulsoup4
    pkgs.python311Packages.streamlit
    pkgs.python311Packages.openai
    pkgs.python311Packages.serpapi
    pkgs.python311Packages.numpy
    pkgs.python311Packages.pandas
  ];
}
