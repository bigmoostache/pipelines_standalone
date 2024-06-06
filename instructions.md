## 1. Handling shared files

To generate a new test file, here is the url:

`https://pipelines.blends.fr/dev/new_url?format=EXTENSION&example=EXAMPLE_FILE_NAME`

This will provide you with a url which you may use to interact with the fresh new, uncorrupted file of the type you are working with.

- `GET` requests to the generated URL will send you a file stream
- `POST` requests to that URL will need to contain an attached `file`, which will replace the previous version.


Therefore, you may corrupt the file. This is why we provided you with an endpoint which will generate fresh uncorrupted examples for you.

## 2. Using the boilerplate

[Here](https://github.com/bigmoostache/visuals) is a `React` boilerplate for a lightweight Web Application whose purpose is to **receive, visualize, manipulate and update** the distant files.

In the boilerplate, the path of interest will be `src/app/(pages)/txt`
You may start by copy pasting that folder, rename it to `src/app/(pages)/plan`, rename `Txt.tsx` to `Plan.tsx`, and then code your UI in there.

To use the boilerplate:
- Install the latest version of `node`
- Run `npm ci`
- Run `npm run dev`

It should launch the application on `localhost:3000`

To check that the setup works well, check that the boilerplate works for the dummy `.txt` visualizer:
- Generate a new file using `https://pipelines.blends.fr/dev/new_url?format=txt&example=example1.txt`, and copy paste the url_encoded url it provides you with.
- Go to `https://localhost:3000/txt?url=<the url encoded url>`
- You should see the Hello yorldm and should be able to modify it.

## 3. The boilerplate is just a boilerplate

If you would rather code in a different langage, I'm ok with it. The requirements of the delivery should just be an app which, on

`https://deploy_url.com/<extension>?url=<the encoded url>`

Provides a nice interface to visualize, manipulate and update the data structure. The boilerplate juste provides yith an example implementation, as well as pre-coded protocols to fetch and update the files.
