/* jshint esversion: 9 */

import React, { useReducer, useContext } from 'react';
import { Grid, Paper, Typography, Divider } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import CssBaseline from '@material-ui/core/CssBaseline';

export { SuperForm };

// Contains all the initial form values
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

// All the valid action types
const types = {
    new: "new",
    validate: "validate"
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

// Reducer function, for use with useReducer hook
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

// Provide reducer dispatch function to all subform elements
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

// Form component for holding overall form data
function SuperForm(props) {
    const classes = useStyles(props);

    const [state, dispatch] = useReducer(reducer, initialForm);

    return (<>
        <Paper elevation={3} className={classes.formContainer}>
            <FormDispatch.Provider value={dispatch}>
                <SubForm buyingParty={state["buyingParty"]}/>
            </FormDispatch.Provider>
        </Paper>
    </>);
}

// Component for text fields in the form
function FormField(props) {
    return <TextField variant="outlined" {...props}/>;
}

// Subform component - only need 4, so can be custom
function SubForm(props) {
    const classes = useStyles(props);

    const dispatch = useContext(FormDispatch);

    const inputChange = input => e => {
        dispatch({
            input: input,
            type: types.new,
            newValue: e.target.value
        });
    };

    return (
    <Grid
            container
            justify="center"
            alignContent="center"
            className={classes.formContainer}
            direction="column"
            spacing={3}
    >
        <CssBaseline />
        <Grid item>
            <Typography variant="h4" gutterBottom>
                Step 1 of 4
            </Typography>
        </Grid>
        <Grid item>
            <FormField
                id="buyingParty"
                label="Buying Party"
                value={props.buyingParty}
                onChange={inputChange(inputs.buying)}
            />
        </Grid>
        <Grid item>
            <FormField
                id="sellingParty"
                label="Selling Party"
                value={props.sellingParty}
                onChange={inputChange(inputs.selling)}
            />
        </Grid>
        <Grid item>
            <FormField
                id="productName"
                label="Product Name"
                value={props.productName}
                onChange={inputChange(inputs.product)}
            />
        </Grid>
    </Grid>
    );
}