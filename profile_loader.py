import os

class Profile:
    def __init__(self, file):
        f = open(file, "r")
        lines = f.readlines()
        for line in lines:
            key = (line.split('=')[0]).strip()
            value = ('='.join(line.split('=')[1:])).strip()
            self.__dict__[key] = value
        f.close()

        if "NAME" not in self.__dict__:
            raise AttributeError("Profile must have a name")
        if "PARSER" not in self.__dict__:
            raise AttributeError("Profile must have a parser")
        if "AGENT" not in self.__dict__:
            raise AttributeError("Profile must have an agent")

    def get_info_dict(self):
        return self.__dict__


items = os.scandir("./Profiles")
profile_list = []
for item in items:
    new_profile = Profile("./Profiles/{0}".format(item.name))
    profile_list.append(new_profile)