import requests

url = "https://paragraph-generator.p.rapidapi.com/paragraph-generator"

querystring = {"topic": "How can I be good at playing League of Legends.",
               "section_heading": ""}

headers = {
    "X-RapidAPI-Key": "dc1bbf0386msh9534735bfd89595p134c19jsn70f75dd00648",
    "X-RapidAPI-Host": "paragraph-generator.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())
