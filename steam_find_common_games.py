import bs4
import urllib.request
import requests
import sys


def add_user(username: str, steamkey: str):
	html_data = urllib.request.urlopen(f"https://steamidfinder.com/lookup/{username}")
	soup = bs4.BeautifulSoup(html_data, 'lxml')
	userinfo = soup.find('div', "panel-body")
	ids = userinfo.find_all("code")
	print(f"using steam id `{ids[2].string}` for custom username `{username}`")
	print(requests.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steamkey}&steamid={ids[2].string}&format=json"))
	steam_games_json = requests.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={steamkey}&steamid={ids[2].string}&format=json").json()["response"]
	print("found", steam_games_json["game_count"], "games")
	out = []
	games_counter = 0
	failed_counter = 0
	unknown_counter = 0
	unknown_with_playtime_counter = 0
	zero_play_counter = 0
	print("+-", "-" * steam_games_json["game_count"], "-+", sep="")
	print("| ", end="", sep="")
	for game in steam_games_json["games"]:
		try:
			needs_store_page = False
			log_char = ""
			gamename = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/?key={steamkey}&appid={game['appid']}&format=json").json()["game"]["gameName"]
			if "ValveTestApp" in gamename:
				if game['playtime_forever'] == 0 or game['playtime_forever'] == "0":
					log_char = "v"
					unknown_counter += 1
				else:
					log_char = "V"
					unknown_with_playtime_counter += 1
				needs_store_page = True
			elif "UntitledApp" in gamename:
				if game['playtime_forever'] == 0 or game['playtime_forever'] == "0":
					log_char = "u"
					unknown_counter += 1
				else:
					log_char = "U"
					unknown_with_playtime_counter += 1
				needs_store_page = True
			elif gamename == "":
				if game['playtime_forever'] == 0 or game['playtime_forever'] == "0":
					log_char = "_"
					unknown_counter += 1
				else:
					log_char = "-"
					unknown_with_playtime_counter += 1
				needs_store_page = True
			else:
				if game['appid'] == 211820 or game['appid'] == "211820":
					gamename = "Starbound"  # both `Starbound` and `Starbound - Unstable` show up as `Starbound - Unstable`
				if game['playtime_forever'] == 0 or game['playtime_forever'] == "0":
					print("0", end="")
					zero_play_counter += 1
				else:
					print("#", end="")
					games_counter += 1
				out.append([game['appid'], gamename, game['playtime_forever']])
			if needs_store_page:
				steam_app_page = urllib.request.urlopen(f"https://store.steampowered.com/app/{game['appid']}")
				app_soup = bs4.BeautifulSoup(steam_app_page, 'lxml')
				try:
					correct_game_name = app_soup.find(class_="apphub_AppName").string
					print(log_char, end="")
					out.append([game['appid'], correct_game_name, game['playtime_forever']])
				except:
					# correct_game_name = "name retrieval from store page failed"
					print("^", end="")
					failed_counter += 1
		except KeyError:
			print("!", end="")
			failed_counter += 1
	print(" |\n+-", "-" * steam_games_json["game_count"], "-+", sep="")
	print("| #/0     added", games_counter + zero_play_counter, "games")
	print("| UV-/uv_ added", unknown_counter + unknown_with_playtime_counter, "games with default or no name using store page (slower)")
	print("| !/^    ", failed_counter, "empty json responses and games without a name retrievable in any way were not added")
	print("+-------------------------------------------")
	print("| added", steam_games_json["game_count"] - failed_counter, "games in total")
	# print("| added", games_counter + zero_play_counter + unknown_counter + unknown_with_playtime_counter, "games in total")
	print("+-------------------------------------------")
	print("numbers may not add up due to failing after a counter was incremented")
	return out


alix = add_user("rocketpoweredtennisball", "add your steam api key here")
print(alix)