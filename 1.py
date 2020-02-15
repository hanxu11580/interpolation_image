import requests

header = {
    'Authorization': 'eyJhbGciOiJSUzI1NiJ9.eyJpZCI6MTU3LCJhY2NvdW50IjoiIiwibmlja25hbWUiOiLmnb7mnpwiLCJuYmYiOjE1ODE0ODc5NTQsImV4cCI6MTU4MTU3NDM1NH0.hGq3a6OIrnt3XkGBgfFREbxAIqfj4n3kGjgJkmrXPcOKZ-Ag5_M6ZmDZYyGyHDBjvMQAz2qCQ_eieseNgNugsNOzyPXpown99pWBxBPoWc6X8QYZpR4T2R9SeA5N4D4A8bVoJfhi0N3ihNVkAoCdOAqkmk6F3PohA5dHqyc6MFrchEL3FIuikKat8CbtDtqnVnO6QnFNwhQGk5wgYgBZ47b76ZuJkE24habgLZkwKKq6dOSGus5tSdXJIvHeeuK8-92phQm6jDJ1DIz6vOTErbFD_7Nx5yI0aDNOuime_OkIiyf4RwTWazhfRoclG9v-t4FlXhIy7TsuHrfDYA9T_Q',
}
url = 'https://dev.meijing.fpi-inc.site/simple-oss-server/api/v1/oss/upload/gas/images'
data = {'file': ('2020-02-07 18_00_00.png', open('./Image_data//aqi//2020-02-07 18_00_00.png', 'rb'), 'image/png', {})}
res = requests.post(url, headers=header, files=data)
print(res.content)


