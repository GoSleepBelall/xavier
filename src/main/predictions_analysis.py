from operator_utils import WeightUtils
import tensorflow as tf
from tensorflow.keras.datasets import mnist
from tensorflow import keras
import numpy as np
from keras.utils import np_utils
from sklearn.metrics import classification_report
from prettytable import PrettyTable


def float_formatter(num):
    return "{:.1f}".format(num)


def matrix_mapper(data, count):
    iteration_number = 0
    print("[", end=" ")
    for x in data:
        print("[", end=" ")
        for y in x:
            print(float_formatter(y), end=" ")
        print("]", end=" ")
        iteration_number = iteration_number + 1
        if iteration_number >= count:
            break
        print()
    print("]")


def classify_weights(single_class, classes):
    classified_data = np_utils.to_categorical(single_class, classes)
    return classified_data


def map_manual_predictions(predictions, test_data, classes, count):
    # In order to map predictions with the labels, we can classify data into 10 classes
    classified_test_data = classify_weights(test_data, classes)
    print("predictions")
    matrix_mapper(predictions, count)
    print("labels")
    matrix_mapper(classified_test_data, count)


def get_confusion_matrix(predictions, labels):
    # Reshaping Predictions (Merging data)
    predictions = np.argmax(predictions, axis=1)

    # Get unique class labels in the labels array
    classes = np.unique(labels)
    # Initialize counters for each class
    counters = {}
    for class_label in classes:
        counters[class_label] = {'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0}

    # Loop over the elements in the predictions and labels arrays
    for i in range(len(predictions)):
        # Get the prediction and label for the current element
        prediction = predictions[i]
        label = labels[i]

        # Increment the appropriate counter based on the prediction and label
        if prediction == label:
            # TRUE-POSITIVE case: Model accurately predicted the label
            counters[prediction]['tp'] += 1
            # TRUE-NEGATIVE case: Model accurately predicted that label does not exist
            for class_label in range(10):
                if class_label != prediction:
                    counters[class_label]['tn'] += 1
        else:
            # Model predicted a wrong label
            counters[prediction]['fp'] += 1
            # Model did not predict the label when it existed
            counters[label]['fn'] += 1
    return counters


def printConfusionMatrix(predictions, labels):
    counters = get_confusion_matrix(predictions, labels)
    table = PrettyTable()
    table.field_names = ['Class', 'True-Positive', 'True-Negative', 'False-Positive', 'False-Negative']

    # Add a row for each class to the table
    for class_label, class_counters in counters.items():
        table.add_row(
            [class_label, class_counters['tp'], class_counters['tn'], class_counters['fp'], class_counters['fn']])
    # Print the table
    print(table)


##################===============================#####################

def printClassificationReport(predictions, labels):
    table = PrettyTable()
    table.field_names = ['Class', 'Accuracy', 'Specificity', 'Sensitivity', 'recall', 'precision', 'f1-score']

    metrics = get_all_metrics(predictions, labels)
    for class_label, class_metrics in metrics.items():
        table.add_row(
            [class_label,
             class_metrics['accuracy'],
             class_metrics['specificity'],
             class_metrics['sensitivity'],
             class_metrics['recall'],
             class_metrics['precision'],
             class_metrics['f1_score']])
    print(table)


def getAccuracy(predictions, labels):
    counters = get_confusion_matrix(predictions, labels)
    accuracy = {}
    for class_label, class_counters in counters.items():
        tp = class_counters['tp']
        tn = class_counters['tn']
        fp = class_counters['fp']
        fn = class_counters['fn']
        accuracy[class_label] = "{:.4f}".format((tp + tn) / (tp + tn + fp + fn))
    return accuracy


def getSpecificity(predictions, labels):
    counters = get_confusion_matrix(predictions, labels)
    specificity = {}
    for class_label, class_counters in counters.items():
        tn = class_counters['tn']
        fp = class_counters['fp']
        specificity[class_label] = "{:.4f}".format(tn / (tn + fp))
    return specificity


def getSensitivity(predictions, labels):
    counters = get_confusion_matrix(predictions, labels)
    sensitivity = {}
    for class_label, class_counters in counters.items():
        tp = class_counters['tp']
        fn = class_counters['fn']
        sensitivity[class_label] = "{:.4f}".format(tp / (tp + fn))
    return sensitivity

def getPrecision(predictions, labels):
    counters = get_confusion_matrix(predictions, labels)
    precision = {}
    for class_label, class_counters in counters.items():
        tp = class_counters['tp']
        fp = class_counters['fp']
        precision[class_label] = "{:.4f}".format(tp / (tp + fp))
    return precision

def getRecall(predictions, labels):
    counters = get_confusion_matrix(predictions, labels)
    recall = {}
    for class_label, class_counters in counters.items():
        tp = class_counters['tp']
        fn = class_counters['fn']
        recall[class_label] = "{:.4f}".format(tp / (tp + fn))
    return recall

def getF1Score(predictions, labels):
    precision = getPrecision(predictions, labels)
    recall = getRecall(predictions, labels)
    f1_score = {}
    for class_label, p in precision.items():
        f1_score[class_label] = "{:.4f}".format(2 * (float(p) * float(recall[class_label])) / (float(p) + float(recall[class_label])))
    return f1_score

def get_model_accuracy(prediction, labels):
    counters = get_confusion_matrix(prediction, labels)
    tp_sum = 0
    tn_sum = 0
    total = 0
    for class_label, class_counters in counters.items():
        tp_sum += class_counters['tp']
        tn_sum += class_counters['tn']
        total += class_counters['tp'] + class_counters['tn'] + class_counters['fp'] + class_counters['fn']
    return (tp_sum + tn_sum) / total

def get_all_metrics(predictions, labels):
    results = {}
    accuracy = getAccuracy(predictions, labels)
    specificity = getSpecificity(predictions, labels)
    sensitivity = getSensitivity(predictions, labels)
    precision = getPrecision(predictions, labels)
    recall = getRecall(predictions, labels)
    f1_score = getF1Score(predictions, labels)

    for class_label in range(10):
        class_results = {
            'accuracy': accuracy[class_label],
            'specificity': specificity[class_label],
            'sensitivity': sensitivity[class_label],
            'precision': precision[class_label],
            'recall': recall[class_label],
            'f1_score': f1_score[class_label]
        }
        results[class_label] = class_results

    return results

def generate_classification_report(predictions, labels):
    # Reshaping Predictions (Merging data)
    predictions = np.argmax(predictions, axis=1)
    # Generate Automatic Classification Report
    print(classification_report(labels, predictions))
