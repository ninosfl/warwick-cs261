/* jshint esversion: 9 */

import React, { useReducer, useContext } from 'react';
import { Grid, Paper, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
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
    validate: "validate",
    correction: "correction"
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
            // Return a new object with only the input modified!
            return { ...state, [action.input]: action.newValue };

        case types.validate:
            // TODO: fetch from API
            return state;

        case types.correction:
            // TODO: Send to API
            return state;

        default:
            return state;
    }
};

// Provide reducer dispatch function to all subform elements
const FormDispatch = React.createContext(null);

// Mad styling son - mostly to ensure the form goes in the middle of the screen
const useStyles = makeStyles( theme => ({
    formContainer: {
        minHeight: "80vh",
        minWidth: "80vh",
        position: 'absolute', 
        left: '50%', 
        top: '50%',
        transform: 'translate(-50%, -50%)'
    },
    formItemContainer: {
        minWidth: "60vh",
    },
    formItem: {
        minWidth: "50vh",
    },
    formTitle: {
        // right: '40%'
    },
    button: {
        margin: theme.spacing(1),
        left: '50%'
    },
}));

// Form component for holding overall form data
function SuperForm(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Use reducer hook to handle form data
    const [state, dispatch] = useReducer(reducer, initialForm);

    // Put form in awesome-looking paper background
    return (
        <Paper elevation={3} className={classes.formContainer}>
            <FormDispatch.Provider value={dispatch}>
                <SubForm fields={{...state}} />
            </FormDispatch.Provider>
        </Paper>
    );
}

// Component for text fields in the form
function FormField(props) {
    // Get dispatch function from the reducer hook via a context hook
    // TODO: Move this out if this proves expensive
    const dispatch = useContext(FormDispatch);

    // Fetch defined styling
    const classes = useStyles(props);

    // Create a function that takes in an event, and dispatches the appropriate
    // action to the reducer hook.
    const handleChange = e => dispatch({
        input: props.input,
        type: types.new,
        newValue: e.target.value
    });

    return (
        <TextField
            variant="outlined"
            onChange={handleChange}
            className={classes.formItem}
            {...props}
        />
    );
}

function NextButton(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    return (
        <Button
            variant="contained"
            color="primary"
            className={classes.button}
            endIcon={<NavigateNextIcon />}
            {...props}
        >
            Next Page
        </Button>
    );
}

function SubFormTitle(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    return (
        <Typography variant="h4" gutterBottom className={classes.formTitle}>
            Step {props.number} of 4
        </Typography>
    );
}

// Subform component - only need 4, so can be custom
function SubForm(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Render sub-form within a grid
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
            <SubFormTitle number={1} />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormField
                id="buyingParty"
                label="Buying Party"
                value={props.fields.buyingParty}
                input={inputs.buying}
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormField
                id="sellingParty"
                label="Selling Party"
                value={props.fields.sellingParty}
                input={inputs.selling}
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormField
                id="productName"
                label="Product Name"
                value={props.fields.productName}
                input={inputs.product}
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            {(props.fields.sellingParty === ""
                || props.fields.buyingParty === ""
                || props.fields.productName === "")
                ? <NextButton disabled /> : <NextButton />}
        </Grid>
    </Grid>
    );
}