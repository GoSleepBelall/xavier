from typing import Union
from fastapi import FastAPI
from fastapi import HTTPException
from fastapi import Response
import sys
import os
import json_tricks as jt
import json
from tensorflow import keras
from keras import models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "main")))
from mutation_operators import NeuronLevel
from operator_utils import WeightUtils
from operator_utils import Model_layers





app = FastAPI()
layers = Model_layers()
weights = WeightUtils()
operator = NeuronLevel()


# Read the models globally

lenet5 = models.load_model("../../models/xavier-lenet5.h5")
alexnet = models.load_model("../../models/xavier-lenet5.h5")       #TODO: this is still reading lenet-5 because i dont have alexnet right now


# A global dictionary mapping model names to model objects
model_dict = {
    'Lenet5': lenet5,
    'Alexnet': alexnet
}

# GET request to retrieve all the trainable weights of a particular layer in a specific model
@app.get("/weights/{modelId}/{layerName}")
def get_weights(modelId: str, layerName: str):
    # Get the model object from the dictionary
    model_var = model_dict.get(modelId)

    # Create a deep copy of the model
    model_obj = models.clone_model(model_var)
    model_obj.set_weights(model_var.get_weights())
    trainable_weights = weights.GetWeights(model_obj, layerName)

    result = trainable_weights.tolist()
    return jt.dumps(result)


# GET request to retrieve all the layers in a specific model
@app.get("/layers/{modelId}")
def get_layers(modelId: str):
    # Get the model object from the dictionary
    model_var = model_dict.get(modelId)

    # Create a deep copy of the model
    model_obj = models.clone_model(model_var)
    model_obj.set_weights(model_var.get_weights())

    layer_names = layers.getLayerNames(model_obj)
    return json.dumps(layer_names)

# GET request to retrieve all the layers on which Neuron level Mutation Operators are applicable
@app.get("/neuron_layers/{modelId}")
def get_neuron_layers(modelId: str):
    # Get the model object from the dictionary
    model_var = model_dict.get(modelId)

    # Create a deep copy of the model
    model_obj = models.clone_model(model_var)
    model_obj.set_weights(model_var.get_weights())

    layer_names = layers.getNeuronLayers(model_obj)
    return json.dumps(layer_names)


# GET request to retrieve all the weights of a specific kernel in a specific layer of a specific model
@app.get("/weights/{modelId}/{layerName}/{kernel}")
def getKernelWeights(modelId: str, layerName: str, kernel: int):
    # Get the model object from the dictionary
    model_var = model_dict.get(modelId)

    # Create a deep copy of the model
    model_obj = models.clone_model(model_var)
    model_obj.set_weights(model_var.get_weights())
    # Get Trainable Weights
    trainable_weights = weights.GetWeights(model_obj, layerName)

    # Get Kernel wise weights from all weights
    kernel_weights = weights.getKernelWeights(trainable_weights, kernel)
    return jt.dumps(kernel_weights)

# GET request to retrieve number of kernels present in a layer
@app.get("/kernel/{modelId}/{layerName}")
def getKernelNum(modelId: str, layerName: str):
    # Get the model object from the dictionary
    model_var = model_dict.get(modelId)

    # Create a deep copy of the model
    model_obj = models.clone_model(model_var)
    model_obj.set_weights(model_var.get_weights())

    return json.dumps(layers.getKernelNumbers(model_obj, layerName))

# GET request to retrieve List of Mutation Operators present
@app.get("/operators-list/{operatortype}")
def getMutationOperatorsList(operatortype: int):
    if operatortype == 1:
        return json.dumps(NeuronLevel.neuronLevelMutationOperatorslist)
    #TODO: add other type of mutation operators when done


# GET request to retrieve Description of Mutation Operators present
@app.get("/operators-description/{type}")
def getMutationOperatorsDescription(operatortype: int):
    if operatortype == 1:
        return jt.dumps(NeuronLevel.neuronLevelMutationOperatorsDescription)
    #TODO: add other type of mutation operators when done


# PUT request to change neuron value using Change Neuron Mutation Operator
@app.put("/change-neuron/{modelId}/{layerName}/{row}/{column}/{kernel}/{value}")
def change_neuron(modelId: str, layerName: str, row: int, column: int, kernel: int, value: float, response: Response):
    # Get the model object from the dictionary
    model_var = model_dict.get(modelId)

    # Create a deep copy of the model
    model_obj = models.clone_model(model_var)
    model_obj.set_weights(model_var.get_weights())
    try:
        operator.changeNeuron(model_obj, layerName, row, column, kernel, value)
        response.status_code = 200
        return {"message": "Neuron value successfully changed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT request to block neuron value using Block Neuron Mutation Operator
@app.put("/block-neuron/{modelId}/{layerName}/{row}/{column}/{kernel}")
def block_neuron(modelId: str, layerName: str, row: int, column: int, kernel: int, response: Response):
    # Get the model object from the dictionary
    model_var = model_dict.get(modelId)

    # Create a deep copy of the model
    model_obj = models.clone_model(model_var)
    model_obj.set_weights(model_var.get_weights())
    try:
        operator.blockNeuron(model_obj, layerName, row, column, kernel)
        response.status_code = 200
        return {"message": "Neuron successfully blocked"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT request to change neuron value with its multiplicative inverse
@app.put("/mul-inverse/{modelId}/{layerName}/{row}/{column}/{kernel}")
def mul_inverse_neuron(modelId: str, layerName: str, row: int, column: int, kernel: int, response: Response):
    # Get the model object from the dictionary
    model_var = model_dict.get(modelId)

    # Create a deep copy of the model
    model_obj = models.clone_model(model_var)
    model_obj.set_weights(model_var.get_weights())
    try:
        operator.mul_inverse(model_obj, layerName, row, column, kernel)
        response.status_code = 200
        return {"message": "Neuron value successfully changed to multiplicative inverse"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT request to replace neuron with its Additive Inverse
@app.put("/additive-inverse/{modelId}/{layerName}/{row}/{column}/{kernel}")
def additive_inverse_neuron(modelId: str, layerName: str, row: int, column: int, kernel: int, response: Response):
    # Get the model object from the dictionary
    model_var = model_dict.get(modelId)

    # Create a deep copy of the model
    model_obj = models.clone_model(model_var)
    model_obj.set_weights(model_var.get_weights())
    try:
        operator.additive_inverse(model_obj, layerName, row, column, kernel)
        response.status_code = 200
        return {"message": "Neuron value successfully changed to additive inverse"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# PUT request to invert the value of neuron using Invert Neuron Mutation Operator
@app.put("/invert-neuron/{modelId}/{layerName}/{row}/{column}/{kernel}")
def invert_neuron(modelId: str, layerName: str, row: int, column: int, kernel: int, response: Response):
    # Get the model object from the dictionary
    model_var = model_dict.get(modelId)

    # Create a deep copy of the model
    model_obj = models.clone_model(model_var)
    model_obj.set_weights(model_var.get_weights())
    try:
        operator.invertNeuron(model_obj, layerName, row, column, kernel)
        response.status_code = 200
        return {"message": "Neuron value successfully inverted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Index based PUT request for Mutation Operators
@app.put("/mutation-operator/{index}/{modelId}/{layerName}/{row}/{column}/{kernel}/{value}")
def mutation_operator(index: int, modelId: str, layerName: str, row: int, column: int, kernel: int, response: Response, value: Union[float, None] = None):

    if index == 1:
        result = change_neuron(modelId, layerName, row, column, kernel, value)
    elif index == 2:
        result = block_neuron(modelId, layerName, row, column, kernel)
    elif index == 3:
        result = mul_inverse_neuron(modelId, layerName, row, column, kernel)
    elif index == 4:
        result = additive_inverse_neuron(modelId, layerName, row, column, kernel)
    elif index == 5:
        result = invert_neuron(modelId, layerName, row, column, kernel)
    else:
        # If the index is not recognized, return an error message
        raise HTTPException(status_code=400, detail="Invalid Mutation Operator index")

    response.status_code = 200
    return {"message": "Mutation operator successfully applied", "result": result}
