/* jshint esversion: 9 */

import React from 'react';
import { makeStyles } from '@material-ui/core/styles';

// All the valid forms
const subForms = {
    1: "1",
    2: "2",
    3: "3",
    "submit": "Submit"
};

const host = "http://localhost:8000/";

// Contains all the initial form values
const initialFormState = {
    "buyingParty": "",
    "sellingParty": "",
    "productName": "",
    "quantity": "",
    "underlyingCurrency": "",
    "underlyingPrice": "",
    "maturityDate": "",
    "notionalCurrency": "",
    "strikePrice": "",
    "currentForm": subForms[1],
    "submitNow": false,
    "validationInputs": [],
    "correctionFields": {
        "buyingParty": [],
        "sellingParty": [],
        "productName": [],
        "quantity": [],
        "underlyingCurrency": [],
        "underlyingPrice": [],
        "maturityDate": [],
        "notionalCurrency": [],
        "strikePrice": [],
        "correctionLog": []
    },
    "incorrectFields": {
        "buyingParty": false,
        "sellingParty": false,
        "productName": false,
        "quantity": false,
        "underlyingCurrency": false,
        "underlyingPrice": false,
        "maturityDate": false,
        "notionalCurrency": false,
        "strikePrice": false,
    },
    "requestingFields": {
        "buyingParty": false,
        "sellingParty": false,
        "productName": false,
        "quantity": false,
        "underlyingCurrency": false,
        "underlyingPrice": false,
        "maturityDate": false,
        "notionalCurrency": false,
        "strikePrice": false,
    },
    "currencies": [],
    "MLError": "",
};

// All the valid action types
const actionTypes = {
    new: "new",
    validate: "validate",
    correction: "correction",
    provideSuggestions: "provideSuggestions",
    markNoSuggestions: "markNoSuggestions",
    markCorrect: "markCorrect",
    nextForm: "next",
    prevForm: "prev",
    populateCurrencies: "populateCurrencies",
    markRequesting: "markRequesting",
    markRequestComplete: "markRequestComplete",
    newMLError: "newMLError"
};

// All the valid input types - expressed here as an enum to avoid strings
const inputs = {
    buying: "buyingParty",
    selling: "sellingParty",
    product: "productName",
    quantity: "quantity",
    uCurr: "underlyingCurrency",
    uPrice: "underlyingPrice",
    mDate: "maturityDate",
    nCurr: "notionalCurrency",
    sPrice: "strikePrice"
};

// Reducer function, for use with useReducer hook.
// Takes in a current state, and an action object (describing the details of
// the action to be undertaken).
// Returns a new state.
const reducer = (state, action) => {
    switch (action.type) {
        case actionTypes.new:
            // Return a new object with only the relevant input modified!
            return { ...state, [action.input]: action.newValue };

        case actionTypes.validate:
            // Change validationInput to activate SuperForm effect hook.
            return { ...state, "validationInputs": [...state.validationInputs, action.validationInput] };

        case actionTypes.correction:
            // Return modified state with log - get effect hook to send values
            // to API!
            return {
                ...state,
                [action.input]: action.newValue,
                "correctionFields": {
                    ...state.correctionFields,
                    [action.input]: [],
                    "correctionLog": [...state.correctionFields.correctionLog,
                                      [action.input, action.oldValue, action.newValue]
                                     ]
                }
            };

        case actionTypes.provideSuggestions:
            // Replace state correction values with new ones
            return { ...state, "correctionFields": {...state.correctionFields, [action.input]: action.suggestions} };

        case actionTypes.markNoSuggestions:
            // Mark a specific input as incorrect
            return { ...state, "incorrectFields": {...state.incorrectFields, [action.input]: true} };

        case actionTypes.markCorrect:
            // Mark a specific input as correct, wiping it in the process
            return { ...state, "incorrectFields": {...state.incorrectFields, [action.input]: false} };

        case actionTypes.markRequesting:
            return { ...state, "requestingFields": {...state.requestingFields, [action.input]: true} };

        case actionTypes.markRequestComplete:
            return { ...state, "requestingFields": {...state.requestingFields, [action.input]: false} };

        case actionTypes.nextForm:
            switch (state.currentForm) {
                case subForms[1]:
                    return { ...state, "currentForm": subForms[2] };
                case subForms[2]:
                    return { ...state, "currentForm": subForms[3] };
                case subForms[3]:
                    return { ...state, "currentForm": subForms.submit };
                case subForms.submit:
                    // Tell effect hook to get submitting
                    return { ...state, "submitNow": true };
                default:
                    return state;
            }
        
        case actionTypes.prevForm:
            switch (state.currentForm) {
                case subForms[2]:
                    return { ...state, "currentForm": subForms[1] };
                case subForms[3]:
                    return { ...state, "currentForm": subForms[2] };
                case subForms.submit:
                    // Tell effect hook to get submitting
                    return { ...state, "currentForm": subForms[3] };
                default:
                    return state;
            }
        
        case actionTypes.populateCurrencies:
            // Given a list of currencies, put it in the form!
            return { ...state, "currencies": action.currencies };

        case actionTypes.newMLError:
            return { ...state, "MLError": action.message };

        default:
            return state;
    }
};

// Provide reducer dispatch function to all subform elements
const FormDispatch = React.createContext(null);

// Mad styling son - mostly to ensure the form goes in the middle of the screen
const useStyles = makeStyles( theme => ({
    formContainer: {
        height: "80vmin",
        width: "80vmin",
        position: 'absolute', 
        left: '50%',
        top: '50%',
        transform: 'translate(-50%, -50%)'
    },
    // submitContainer: {
    //     minHeight: "90vmin",
    //     width: "80vmin",
    //     position: 'absolute', 
    //     left: '50%',
    //     top: '50%',
    //     transform: 'translate(-50%, -50%)'
    // },
    submitItemContainer: {
        width: "60vmin",
    },
    submitButton: {
        width: "60vmin",
        marginTop: "16px",
    },
    formItemContainer: {
        width: "60vmin",
    },
    formItem: {
        width: '100%'
    },
    formTitle: {
        // right: '40%'
    },
    button: {
        float: 'right'
    },
}));

const all_zeroes = /^0*(0|\.)0*$/;
const int_re = /^\d+$/;
const decimal_re = /^\d+(\.\d{1,2})?$/;
const date_format_re = /^\d{1,2}\/\d{1,2}\/(\d{4}|\d{2})$/;

export {
    subForms,
    initialFormState,
    actionTypes,
    inputs,
    reducer,
    FormDispatch,
    useStyles,
    all_zeroes,
    int_re,
    decimal_re,
    date_format_re,
    host
};