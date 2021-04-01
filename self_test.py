from platonus_api_wrapper import PlatonusAPI
platonus_session = PlatonusAPI("http://92.46.185.146:8080")
#platonus_session.login("Салкимбаев_Сүйеніш", "1A6@")
print(platonus_session.profile.profile_fio())
