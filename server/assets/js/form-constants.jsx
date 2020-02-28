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

// Contains all the initial form values
const initialFormState = {
    "buyingParty": "",
    "sellingParty": "",
    "productName": "",
    "quantity": 0,
    "underlyingCurrency": "",
    "underlyingPrice": "",
    "maturityDate": "01.01.1970",
    "notionalCurrency": "USD",
    "strikePrice": 0.0,
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
        "correctionLog": false
    },
    "currencies": [],
};

// All the valid action types
const actionTypes = {
    new: "new",
    validate: "validate",
    correction: "correction",
    provideSuggestions: "provideSuggestions",
    markIncorrect: "markIncorrect",
    markCorrect: "markCorrect",
    nextForm: "next",
    populateCurrencies: "populateCurrencies"
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

        // FIXME: Cannot validate the same item multiple times in a row.
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

        case actionTypes.markIncorrect:
            // Mark a specific input as incorrect
            return { ...state, "incorrectFields": {...state.incorrectFields, [action.input]: true} };

        case actionTypes.markCorrect:
            // Mark a specific input as correct, wiping it in the process
            return { ...state, "incorrectFields": {...state.incorrectFields, [action.input]: false} };

        case actionTypes.nextForm:
            switch (state.currentForm) {
                case subForms[1]:
                    return { ...state, "currentForm": subForms[2] };
                case subForms[2]:
                    // TODO: Forward to third subform (once it's made lol)
                    return { ...state, "currentForm": subForms.submit };
                case subForms[3]:
                    return { ...state, "currentForm": subForms.submit };
                case subForms.submit:
                    // Tell effect hook to get submitting
                    return { ...state, "submitNow": true };
                default:
                    return state;
            }
            break;
        
        case actionTypes.populateCurrencies:
            // Given a list of currencies, put it in the form!
            return { ...state, "currencies": action.currencies };

        default:
            return state;
    }
};

// Provide reducer dispatch function to all subform elements
const FormDispatch = React.createContext(null);

// Mad styling son - mostly to ensure the form goes in the middle of the screen
const useStyles = makeStyles( theme => ({
    formContainer: {
        height: "90vh",
        width: "80vh",
        position: 'absolute', 
        left: '50%',
        top: '50%',
        transform: 'translate(-50%, -50%)'
    },
    // submitContainer: {
    //     minHeight: "90vh",
    //     width: "80vh",
    //     position: 'absolute', 
    //     left: '50%',
    //     top: '50%',
    //     transform: 'translate(-50%, -50%)'
    // },
    submitItemContainer: {
        width: "60vh",
    },
    submitButton: {
        width: "60vh",
        marginTop: "16px",
    },
    formItemContainer: {
        width: "60vh",
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

export {
    subForms,
    initialFormState,
    actionTypes,
    inputs,
    reducer,
    FormDispatch,
    useStyles
};