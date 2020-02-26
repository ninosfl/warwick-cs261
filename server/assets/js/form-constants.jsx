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
    "underlyingCurrency": "USD",
    "underlyingPrice": 0.0,
    "maturityDate": "01.01.1970",
    "notionalCurrency": "USD",
    "strikePrice": 0.0,
    "currentForm": subForms[1],
    "validationInput": null,
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
};

// All the valid action types
const actionTypes = {
    new: "new",
    validate: "validate",
    correction: "correction",
    provideSuggestions: "provideSuggestions",
    nextForm: "next"
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
            return { ...state, "validationInput": action.validationInput };

        case actionTypes.correction:
            // Log old and new values, to be sent to API
            let log = state.correctionFields.correctionLog;
            log.push([action.input, action.oldValue, action.newValue]);

            // Return modified state with log
            return {
                ...state,
                [action.input]: action.newValue,
                "correctionFields": {
                    ...state.correctionFields,
                    [action.input]: [],
                    "correctionLog": log
                }
            };

        case actionTypes.provideSuggestions:
            // Replace state correction values with new ones
            return { ...state, "correctionFields": {...state.correctionFields, [action.input]: action.suggestions} };

        case actionTypes.nextForm:
            switch (state.currentForm) {
                case subForms[1]:
                    // TODO: Forward to second subform (once it's made lol)
                    return { ...state, "currentForm": subForms.submit };
                case subForms[2]:
                    return { ...state, "currentForm": subForms[3] };
                case subForms[3]:
                    return { ...state, "currentForm": subForms.submit };
                case subForms.submit:
                    // TODO: Submit stuffs
                    return state;
                default:
                    return state;
            }
            break;

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

export { subForms, initialFormState, actionTypes, inputs, reducer, FormDispatch, useStyles };