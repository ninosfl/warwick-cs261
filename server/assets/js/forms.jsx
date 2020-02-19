/* jshint esversion: 9 */

import React, { useReducer, useContext } from 'react';
import { Grid, Paper } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import CssBaseline from '@material-ui/core/CssBaseline';

export { SuperForm };

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
    new: "new",
    validate: "validate"
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
            // Return a new object with the input modified!
            return { ...state, [action.input]: action.newValue };

        case types.validate:
            // TODO: fetch from API
            return state;

        default:
            return state;
    }
};

const FormDispatch = React.createContext(null);

const useStyles = makeStyles({
    formContainer: {
        minHeight: "80vh",
        minWidth: "80vh",
        position: 'absolute', 
        left: '50%', 
        top: '50%',
        transform: 'translate(-50%, -50%)'
    },
});

function SuperForm(props) {
    const classes = useStyles(props);

    const [state, dispatch] = useReducer(reducer, initialForm);

    return (<>
        <Paper elevation={3} className={classes.formContainer}>
            <Grid
                container
                justify="center"
                alignContent="center"
                className={classes.formContainer}
            >
                <CssBaseline />
                <FormDispatch.Provider value={dispatch}>
                    <SubForm buyingParty={state["buyingParty"]}/>
                </FormDispatch.Provider>
            </Grid>
        </Paper>
    </>);
}

function SubForm(props) {
    const dispatch = useContext(FormDispatch);

    const handleChange = e => {
        dispatch({
            input: inputs.buying,
            type: types.new,
            newValue: e.target.value
        });
    };

    return (
        <TextField
            id="buyingParty"
            label="Buying Party"
            value={props.buyingParty}
            onChange={handleChange}
            variant="outlined"
        />
    );
}