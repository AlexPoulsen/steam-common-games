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
			elif "Test App" in gamename:
				if game['playtime_forever'] == 0 or game['playtime_forever'] == "0":
					log_char = "t"
					unknown_counter += 1
				else:
					log_char = "T"
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
	print("| #/0       added", games_counter + zero_play_counter, "games")
	print("| UVT-/uvt_ added", unknown_counter + unknown_with_playtime_counter, "games with default or no name using store page (slower)")
	print("| !/^      ", failed_counter, "empty json responses and games without a name retrievable in any way were not added")
	print("+-------------------------------------------")
	print("| added", steam_games_json["game_count"] - failed_counter, "games in total")
	# print("| added", games_counter + zero_play_counter + unknown_counter + unknown_with_playtime_counter, "games in total")
	print("+-------------------------------------------")
	print("numbers may not add up due to failing after a counter was incremented")
	return out


user1 = add_user("username1", "add your steam api key here")
print(user1)
user2 = add_user("username2", "add your steam api key here")
print(user2)
									

user1.append([875239572, "Minecraft", 60000])


def find_shared(percent: float = 0.8, min_minutes: int = 5, *users):
	longest_index = -1
	longest_len = -1
	for index, user in enumerate(users):
		user.sort()
		if len(user) > longest_len:
			longest_len = len(user)
			longest_index = index
	# users[0], users[longest_index] = users[longest_index], users[0]
	users = [users[longest_index], *users[:longest_index], *users[longest_index+1:]]
	matches = []
	for user in users[1:]:
		user_matches = []
		for game in users[0]:
			for game2 in user:
				if game[0] == game2[0]:  # steam appid matches
					user_matches.append(game2)
					break
		matches.append(user_matches)
	if len(matches) == 1:  # only two users were entered
		return matches[0]
	else:
		all_games_no_playtime = []
		game_playtime = []
		users_with_game = []
		for user_matches in matches:
			for game in user_matches:
				# print(game[1])
				if game[0:2] in all_games_no_playtime:
					users_with_game[all_games_no_playtime.index(game[0:2])] += 1
					# print("incrementing game", game[1])
					game_playtime[all_games_no_playtime.index(game[0:2])] += game[2]
				else:
					all_games_no_playtime.append(game[0:2])
					users_with_game.append(2)
					game_playtime.append(game[2])
		# for i, game in enumerate(all_games):
		# 	print(game[1], ", with ", users_with_game[i], " users", sep="")
		out = []
		for i, game in enumerate(all_games_no_playtime):
			if users_with_game[i] / len(users) >= percent:
				if game_playtime[i] >= min_minutes:
					game.append(game_playtime[i])
					out.append(game)
		return out


def prettify(input_list, limit: int = -1):
	temp_list = []
	for game in input_list:
		temp_list.append([game[2], game[1]])
	temp_list.sort()
	temp_list.reverse()
	if limit < 0:
		for game in temp_list:
			print(game[1])
	else:
		counter = 0
		for game in temp_list:
			print(game[1])
			counter += 1
			if counter >= limit:
				break


prettify(find_shared(0.7, 5, user1, user2))
