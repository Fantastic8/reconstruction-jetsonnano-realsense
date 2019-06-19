
source_folder=${1:-"."}
scp -p22 "$source_folder"/*.png "$USER"@34.74.210.138:scp