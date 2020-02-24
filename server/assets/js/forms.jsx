/* jshint esversion: 9 */

import React, { useReducer, useContext, useEffect, useState } from 'react';
import { Grid, Paper, Typography } from '@material-ui/core';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import PublishIcon from '@material-ui/icons/Publish';
import CssBaseline from '@material-ui/core/CssBaseline';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import { subForms, validationTypes, initialFormState, actionTypes, inputs, reducer, FormDispatch, useStyles } from './form-constants';

export { SuperForm };

// Form component for holding overall form data
function SuperForm(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Use reducer hook to handle form data
    const [state, dispatch] = useReducer(reducer, initialFormState);

    // Use effect hook for api validation
    // No need to reset validationType to some default value, since this
    // effect will only run when it changes.
    useEffect(() => {
        // TODO: Make this do mad fetching to get validated values
        switch (state.validationType) {
            case validationTypes.buying:
                // TODO: Validate buying party!

                // TODO: Make this condition actually API-related
                if (state.buyingParty.includes("test")) {
                    dispatch({
                        type: actionTypes.provideSuggestions,
                        field: inputs.buying,
                        suggestions: ["Sixty", "Nine", "Dudes!"]
                    });
                } else { // TODO: Remove, this is just for debugging
                    dispatch({
                        input: inputs.buying,
                        type: actionTypes.new,
                        newValue: state[inputs.buying] + " (validated by buying)"
                    });
                }

                break;

            case validationTypes.selling:
                // TODO: Validate selling party!

                // TODO: Make this condition actually API-related
                if (state.sellingParty.includes("test")) {
                    dispatch({
                        type: actionTypes.provideSuggestions,
                        field: inputs.selling,
                        suggestions: ["Whoa", "Excellent", "*Electric Guitar Noises*"]
                    });
                } else { // TODO: Remove, this is just for debugging
                    dispatch({
                        input: inputs.selling,
                        type: actionTypes.new,
                        newValue: state[inputs.selling] + " (validated by selling)"
                    });
                }

                break;

            case validationTypes.product:
                // TODO: Validate product!

                // Dispatch validated values to form!
                dispatch({
                    input: inputs.buying,
                    type: actionTypes.new,
                    newValue: state[inputs.buying] + " (validated by product)"
                });
                dispatch({
                    input: inputs.selling,
                    type: actionTypes.new,
                    newValue: state[inputs.selling] + " (validated by product)"
                });
                dispatch({
                    input: inputs.product,
                    type: actionTypes.new,
                    newValue: state[inputs.product] + " (validated by product)"
                });

                break;

            default:
                break;
        }
    }, [state.validationType]);  // Only perform effect when validationType changes

    // Use effect hook for logging corrections!
    useEffect(() => {
        // TODO: Send values to api/correction/
    }, [state.correctionFields]);  // Only perform effect when correctionFields changes

    // Render the specific subform that's currently meant to be on screen
    let elem = null;
    switch (state.currentForm) {
        case subForms[1]:
            elem = (
                <Paper elevation={3} className={classes.formContainer}>
                    <FormDispatch.Provider value={dispatch}>
                        <SubFormOne fields={{...state}} />
                    </FormDispatch.Provider>
                </Paper>
            );
            break;

        case subForms[2]:
            // TODO: Implement sub form 2!
            elem = null;
            break;

        case subForms[3]:
            // TODO: Implement sub form 3!
            elem = null;
            break;

        case subForms.submit:
            elem = (
                <Paper elevation={3} className={classes.formContainer}>
                    <FormDispatch.Provider value={dispatch}>
                        <SubmitForm fields={{...state}} />
                    </FormDispatch.Provider>
                </Paper>
            );
            break;
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
        type: actionTypes.new,
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

// Component for text fields that need correction in the form
function ErrorFormField(props) {
    // Set the anchor element on the menu
    const [anchor, setAnchor] = React.useState(null);

    // Functions for setting the menu anchor to the current form field
    const whenFocused = event => setAnchor(event.currentTarget);
    // TODO: When leaving, dispatch with type actionTypes.correction ??
    const whenLeaving = () => setAnchor(null);

    // Make suggestions React elements
    const suggestions = props.suggestions.map((s, i) =>
        <MenuItem onClick={whenLeaving} key={i}>{s}</MenuItem>
    );

    return (
    <>
        <FormField error helperText="Click here to see correction values" aria-controls="simple-menu" aria-haspopup="true" onClick={whenFocused} {...props}/>
        <Menu
            id="simple-menu"
            anchorEl={anchor}
            keepMounted
            open={Boolean(anchor)}
            onClose={whenLeaving}
        >
            <MenuItem disabled={true}>Please select a correction:</MenuItem>
            {suggestions}
            <MenuItem onClick={whenLeaving}>Stick with: {props.value}</MenuItem>
        </Menu>
    </>);
}

function FormFieldWrapper(props) {
    // Display field normally if no suggestions available
    if (props.suggestions.length === 0) {
        return (
            <FormField
                id={props.id}
                label={props.label}
                value={props.value}
                onBlur={props.onBlur}
            />);

    } else { // Otherwise, return an error field
        return (
            <ErrorFormField
                id={props.id}
                label={props.label}
                value={props.value}
                onBlur={props.onBlur}
                suggestions={props.suggestions}
            />);
    }
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
        type: actionTypes.new,
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

    // Event function to get the SuperForm to render the next SubForm
    const goToNextForm = () => dispatch({ type: actionTypes.nextForm });

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

// First subform component - only need 3, so can be custom
function SubFormOne(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Fetch dispatch function from context
    const dispatch = useContext(FormDispatch);

    // Define functions for validating each field, stating which fields need
    // to be sent and checked
    const validateBuying = () => {
        dispatch({ type: actionTypes.validate, validationType: validationTypes.buying })
    };

    const validateSelling = () => {
        dispatch({ type: actionTypes.validate, validationType: validationTypes.selling })
    };

    const validateProduct = () => {
        dispatch({ type: actionTypes.validate, validationType: validationTypes.product })
    };

    // Flag for if any corrections are required
    let canProgress = (
        props.fields.correctionFields[inputs.buying].length > 0
        || props.fields.correctionFields[inputs.selling].length > 0
        || props.fields.correctionFields[inputs.product].length > 0
        || props.fields.sellingParty === ""
        || props.fields.buyingParty === ""
        || props.fields.productName === ""
    );

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
            <FormFieldWrapper
                id={inputs.buying}
                label="Buying Party"
                value={props.fields.buyingParty}
                onBlur={validateBuying}
                suggestions={props.fields.correctionFields[inputs.buying]}
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormFieldWrapper
                id={inputs.selling}
                label="Selling Party"
                value={props.fields.sellingParty}
                onBlur={validateSelling}
                suggestions={props.fields.correctionFields[inputs.selling]}
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormFieldWrapper
                id={inputs.product}
                label="Product Name"
                value={props.fields.productName}
                onBlur={validateProduct}
                suggestions={props.fields.correctionFields[inputs.product]}
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            {canProgress ? <NextButton disabled /> : <NextButton />}
        </Grid>
    </Grid>
    );
}

// Subform for the final Submit page, where the user checks everything
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
