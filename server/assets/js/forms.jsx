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

const reducer = (state, action) => {
    switch (action.type) {
        case "newbuyingParty":
            break;
    }
};

function SuperForm(props) {
    const [state, dispatch] = useReducer(reducer, initialForm);
    return <h1>Not implemented</h1>;
}

function SubForm(props) {

}