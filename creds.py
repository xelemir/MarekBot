import pylast

bot_token = "<DISCORD_BOT_TOKEN>"

client_id_spotify = "<SPOTIFY_CLIENT_ID>"
client_secret_spotify = "<SPOTIFY_CLIENT_SECRET>"
redirect_uri_spotify = "<SPOTIFY_REDIRECT_URI>"

admin_ids = ["<ADMIN_ID_1>", "<ADMIN_ID_2>"] # these users will be able to use all commands
admin_channel = "<ADMIN_CHANNEL_ID>" # this channel will get support messages initiated by the /feedback command
bot_id = "<BOT_ID>"

trusted_servers = ["<TRUSTED_SERVER_ID_1>", "<TRUSTED_SERVER_ID_2>"] # these servers will be able to use all /jkg commands without fitlering

api_key_imagga = "<IMAGGA_API_KEY>"
api_secret_imagga = "<IMAGGA_API_SECRET>"

api_key_lastfm = "<LASTFM_API_KEY>"
api_secret_lastfm = "<LASTFM_API_SECRET>"

username_lastfm = "<LASTFM_USERNAME>"
password_hash_lastfm = pylast.md5("<LASTFM_PASSWORD_HASH>")

gcpConfig = {
    "host": "<HOST_GCP_MYSQL>",
    "user": "<USER_GCP_MYSQL>",
    "password": "<PASSWORD_GCP_MYSQL>",
    "database": "<DATABASE_GCP_MYSQL>"
}

localConfig = {
    "host": "<HOST_LOCAL_MYSQL>",
    "user": "<USER_LOCAL_MYSQL>",
    "password": "<PASSWORD_LOCAL_MYSQL>",
    "database": "<DATABASE_LOCAL_MYSQL>"
}