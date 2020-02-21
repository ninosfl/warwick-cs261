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

// All the types of validations that can occur
const validationTypes = {
    none: "None",
    buying: "buyingParty",
    selling: "sellingParty",
    product: "buyingParty, sellingParty, product"
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
    "validationType": validationTypes.none
};

// All the valid action types
const actionTypes = {
    new: "new",
    validate: "validate",
    correction: "correction",
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
            // Change validationType to activate SuperForm effect hook.
            return { ...state, "validationType": action.validationType };

        case actionTypes.correction:
            // TODO: Send previous value and new value to API
            return state;

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
        minHeight: "90vh",
        minWidth: "80vh",
        position: 'absolute', 
        left: '50%',
        top: '50%',
        transform: 'translate(-50%, -50%)'
    },
    submitContainer: {
        minHeight: "90vh",
        minWidth: "80vh",
        position: 'absolute', 
        left: '50%',
        top: '50%',
        transform: 'translate(-50%, -50%)'
    },
    submitItemContainer: {
        minWidth: "60vh",
    },
    submitButton: {
        minWidth: "60vh",
        marginTop: "16px",
    },
    formItemContainer: {
        minWidth: "60vh",
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

export { subForms, validationTypes, initialFormState, actionTypes, inputs, reducer, FormDispatch, useStyles };