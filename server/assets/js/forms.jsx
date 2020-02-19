/* jshint esversion: 6 */

import React from 'react';

const initialForm = {
    "buyingParty": "",
    "sellingParty": "",
    "productName": "",
    "quantity": "",
    "underlyingCurrency": "USD",
    "underlyingPrice": 0.0,
    "maturityDate": "01.01.1970",
    "notionalCurrency": "USD",
    "strikePrice": 0.0
};

const types = {
    new: "new"
};

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

const reducer = (state, action) => {
    switch (action.type) {
        case types.new:
            state[action.input] = action.newValue;
            return state;

        default:
            return state;
    }
};

const FormDispatch = React.createContext(null);

function SuperForm(props) {
    const [state, dispatch] = useReducer(reducer, initialForm);

    return (
        <FormDispatch.Provider value={dispatch}>
            <h1>Not implemented yet.</h1>
        </FormDispatch.Provider>
    );
}

function SubForm(props) {

}