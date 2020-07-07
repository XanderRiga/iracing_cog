# iRacing Cog
This is a cog for the Red-Discord Bot that allows users to view and compare their iRacing data directly inside of discord.

## Commands
### !saveid <iRacing Client ID\>
Use this command to save your iRacing ID to your discord ID.

### !recentraces <iRacing Client ID \>
This gives detailed information on the last 10 races of the given user.
If no iRacing Client ID is provided, it will default to the saved ID of the user who called it.
If the user who called it has not saved their ID, then they must provide an ID when calling.

### !update
This will update the saved information for all users in the discord for use of the `!leaderboard` command.
All discords are automatically updated every hour, so often this is unnecessary to run.

**NOTE:** The iRacing API does not update, so even if you finished a race recently and expect to see changes, 
it can take up to a day for those to come through on the bot.

### !leaderboard <category\> <type\>
This prints a leaderboard of all users with saved IDs(through the `!saveid` command) for the given category and type.
Category can be any of `road`, `oval`, `dirtroad`, and `dirtoval`, but it defaults to `road`.
Type is either `career` or `yearly`, and it defaults to career. `career` will show all time data, 
and `yearly` will only show data from the current year.

**NOTE:** This can be called with a category and no type, but if you want to call with a type, you need to pass a category.
For instance, I can call `!leaderboard oval`, but if I want the road leaderboard yearly I need to specify: `!leaderboard road yearly`, `!leaderboard yearly` is **NOT** valid.

### !careerstats <iRacing Client ID\>
This will give an overview of the career stats of the player with the given iRacing Client ID.
If an iRacing Client ID is not provided, then it will use the saved ID for the user who called the command.
If the user has not saved their ID, they must provide an iRacing Client ID.

### !yearlystats <iRacing Client ID\>
This will give an overview of the yearly stats of the player with the given iRacing Client ID.
If an iRacing Client ID is not provided, then it will use the saved ID for the user who called the command.
If the user has not saved their ID, they must provide an iRacing Client ID.
