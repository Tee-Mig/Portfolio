from ft_package.my_package import count_in_list


def test_ft_package():
    print(count_in_list(["toto", "tata", "toto"], "toto"))
    print(count_in_list(["toto", "tata", "toto"], "tutu"))


if __name__ == "__main__":
    test_ft_package()
