import os


@app.route('/process', methods=['POST'])
def process():
    """
    A Function to process data sent from Javascript using Python Code
    :return: data from the page's javascript that has been worked on with python code
    """
    data = request.get_json() # retrieve the data sent from JavaScript
    # process the data using Python code
    result = data['value'] * 2
    return jsonify(result=result) # return the result to JavaScript


@app.route("/receiver", methods=["POST"])
def postME():
    """
    A function to indicate that json data has been receieved via a python call
    :return: should print json data in the browser debug console
    """
    jsonData = request.get_json()
    print(jsonData)
    jsonData = jsonify(jsonData)
    print(data)
    templateData={
        'data':data,
    }
    return jsonData