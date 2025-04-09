# PM
 a productmeta demo

## BackEnd
 This is a web project developed using the Django backend.
 The backend code is stored in the `test` folder.
### Configuration Settings
 Before using this project, you must ensure that you have an **Azure OpenAI endpoint** and **API KEY**. Additionally, a **photo search API** provided by https://www.pexels.com is required.
 
 All the configurations are set in the `test/metaproduct/metaapp/views.py` file. You can adjust the necessary settings here, such as adding or modifying the Azure OpenAI endpoint, API KEY, and Pexels API.

 在使用这个项目之前，你必须确保拥有 Azure OpenAI 的端点（endpoint）和 API 密钥（API KEY）。此外，还需要来自 https://www.pexels.com 的图片搜索 API。

 所有的配置都在 `test/metaproduct/metaapp/views.py` 文件中设置。你可以在这里调整所需的设置，例如添加或修改 Azure OpenAI 的端点、API 密钥和 Pexels API。

## FrontEnd
 The frontend code is located in the `dist` folder.
 The communication between the front end and the back end utilizes **REST API**.
 
 Currently, the address used by the front end is `127.0.0.1` If you need to modify this address, you should do so in the `index-CMzJzzyC.js` and `index-legacy-CIOJkSqZ.js` files.
 
 目前前端使用的地址是 `127.0.0.1`。如果你需要修改这个地址，应当在 `index-CMzJzzyC.js` 和 `index-legacy-CIOJkSqZ.js` 文件中进行修改。 