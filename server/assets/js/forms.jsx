/* jshint esversion: 9 */

import React, { useReducer, useContext } from 'react';
import { Grid, Paper, Typography } from '@material-ui/core';
import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import PublishIcon from '@material-ui/icons/Publish';
import CssBaseline from '@material-ui/core/CssBaseline';

export { SuperForm };

// All the valid forms
const formTypes = {
    1: "1",
    "submit": "Submit"
};

// Contains all the initial form values
const initialForm = {
    "buyingParty": "",
    "sellingParty": "",
    "productName": "",
    "quantity": 0,
    "underlyingCurrency": "USD",
    "underlyingPrice": 0.0,
    "maturityDate": "01.01.1970",
    "notionalCurrency": "USD",
    "strikePrice": 0.0,
    "currentForm": formTypes[1]
};

// All the valid action types
const types = {
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

        case types.nextForm:
            if ((state.currentForm) === formTypes[1]) {
                // TODO: Forward to second subform
                return {...state, "currentForm": formTypes.submit };
            } else if (state.currentForm === formTypes.submit) {
                // TODO: Submit stuffs
                return state;
            }

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

// Form component for holding overall form data
function SuperForm(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Use reducer hook to handle form data
    const [state, dispatch] = useReducer(reducer, initialForm);

    let elem = <p>Stuff went wrong.</p>
    if (state.currentForm === formTypes[1]) {
        elem = (
            <Paper elevation={3} className={classes.formContainer}>
                <FormDispatch.Provider value={dispatch}>
                    <SubForm fields={{...state}} />
                </FormDispatch.Provider>
            </Paper>
        );
    } else if (state.currentForm === formTypes.submit) {
        elem = (
            <Paper elevation={3} className={classes.submitContainer}>
                <FormDispatch.Provider value={dispatch}>
                    <SubmitForm fields={{...state}} />
                </FormDispatch.Provider>
            </Paper>
        );
    }

    return elem;
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
        input: props.id,
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

function SubmitField(props) {
    // Get dispatch function from the reducer hook via a context hook
    // TODO: Move this out if this proves expensive
    const dispatch = useContext(FormDispatch);

    // Fetch defined styling
    const classes = useStyles(props);

    // Create a function that takes in an event, and dispatches the appropriate
    // action to the reducer hook.
    const handleChange = e => dispatch({
        input: props.id,
        type: types.new,
        newValue: e.target.value
    });

    return (
        <TextField
            variant="standard"
            size="small"
            onChange={handleChange}
            className={classes.formItem}
            {...props}
        />
    );
}

function NextButton(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Fetch dispatch function from context
    const dispatch = useContext(FormDispatch);

    const goToNextForm = () => dispatch({ type: types.nextForm });

    return (
        <Button
            variant="contained"
            color="primary"
            className={classes.button}
            endIcon={<NavigateNextIcon />}
            onClick={goToNextForm}
            {...props}
        >
            Next Page
        </Button>
    );
}

function SubmitButton(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    return (
        <Button
            variant="contained"
            color="primary"
            className={classes.button}
            endIcon={<CloudUploadIcon />}
            // endIcon={<PublishIcon />}
            {...props}
        >
            Submit
        </Button>
    );
}

function SubFormTitle(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    return (
        <Typography variant="h4" gutterBottom className={classes.formTitle} {...props}/>
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
            <SubFormTitle>Step 1 of 4</SubFormTitle>
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormField
                id={inputs.buying}
                label="Buying Party"
                value={props.fields.buyingParty}
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormField
                id={inputs.selling}
                label="Selling Party"
                value={props.fields.sellingParty}
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormField
                id={inputs.product}
                label="Product Name"
                value={props.fields.productName}
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

function SubmitForm(props) {
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
            spacing={0}
        >
            <Grid item>
                <SubFormTitle>Final Check</SubFormTitle>
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <SubmitField
                    id={inputs.buying}
                    label="Buying Party"
                    value={props.fields.buyingParty}
                />
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <SubmitField
                    id={inputs.selling}
                    label="Selling Party"
                    value={props.fields.sellingParty}
                />
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <SubmitField
                    id={inputs.product}
                    label="Product Name"
                    value={props.fields.productName}
                />
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <SubmitField
                    id={inputs.quantity}
                    label="Product Quantity"
                    value={props.fields.quantity}
                />
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <SubmitField
                    id={inputs.uPrice}
                    label="Underlying Price"
                    value={props.fields.underlyingPrice}
                />
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <SubmitField
                    id={inputs.uCurr}
                    label="Underlying Currency"
                    value={props.fields.underlyingCurrency}
                />
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <SubmitField
                    id={inputs.mDate}
                    label="Maturity Date"
                    value={props.fields.maturityDate}
                />
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <SubmitField
                    id={inputs.nCurr}
                    label="Notional Currency"
                    value={props.fields.notionalCurrency}
                />
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <SubmitField
                    id={inputs.sPrice}
                    label="Strike Price"
                    value={props.fields.strikePrice}
                />
            </Grid>
            <Grid item className={classes.submitButton}>
                <SubmitButton/>
            </Grid>
        </Grid>
    );
}