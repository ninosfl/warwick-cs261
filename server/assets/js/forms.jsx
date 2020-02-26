/* jshint esversion: 9 */

import React, { useReducer, useContext, useEffect, useState } from 'react';
import { Grid, Paper, Typography } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { subForms, initialFormState, actionTypes, inputs, reducer, FormDispatch, useStyles } from './form-constants';
import { FormFieldWrapper, SubmitField, SubmitButton, NextButton, SubFormTitle } from './form-components';

export { SuperForm };


// Form component for holding overall form data
function SuperForm(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Use reducer hook to handle form data
    const [state, dispatch] = useReducer(reducer, initialFormState);

    // Use effect hook for api validation
    // No need to reset validationInput to some default value, since this
    // effect will only run when it changes.
    useEffect(() => {
        // TODO: Make this do mad fetching to get validated values
        switch (state.validationInput) {
            case inputs.buying:
                // TODO: Validate buying party!

                // TODO: Make this condition actually API-related
                if (state.buyingParty.includes("test")) {
                    dispatch({
                        type: actionTypes.provideSuggestions,
                        input: inputs.buying,
                        suggestions: ["Sixty", "Nine", "Dudes!"]
                    });
                }

                break;

            case inputs.selling:
                // TODO: Validate selling party!

                // TODO: Make this condition actually API-related
                if (state.sellingParty.includes("test")) {
                    dispatch({
                        type: actionTypes.provideSuggestions,
                        input: inputs.selling,
                        suggestions: ["Whoa", "Excellent", "*Electric Guitar Noises*"]
                    });
                }

                break;

            case inputs.product:
                // TODO: Validate product!

                if (state.productName.includes("test")) {
                    dispatch({
                        type: actionTypes.provideSuggestions,
                        input: inputs.product,
                        suggestions: ["Strange things are", "afoot at", "the Circle-K"]
                    });
                }
                // // Dispatch validated values to form!
                // dispatch({
                //     input: inputs.buying,
                //     type: actionTypes.new,
                //     newValue: state[inputs.buying] + " (validated by product)"
                // });
                // dispatch({
                //     input: inputs.selling,
                //     type: actionTypes.new,
                //     newValue: state[inputs.selling] + " (validated by product)"
                // });
                // dispatch({
                //     input: inputs.product,
                //     type: actionTypes.new,
                //     newValue: state[inputs.product] + " (validated by product)"
                // });            

                break;

            // TODO: Below validations!

            case inputs.quantity:
                break;

            case inputs.uCurr:
                break;

            case inputs.uPrice:
                break;
            
            case inputs.mDate:
                break;
            
            case inputs.nCurr:
                break;
            
            case inputs.sPrice:
                break;

            default:
                break;
        }
    }, [state.validationInput]);  // Only perform effect when validationInput changes

    // Use effect hook for logging corrections!
    useEffect(() => {
        const [field, oldVal, newVal] = state.correctionFields.correctionLog.slice(-1);
        // TODO: Send fields to API!
    }, [state.correctionFields.correctionLog]);  // Only perform effect when correctionFields changes

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


// First subform component - only need 3, so can be custom
function SubFormOne(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Fetch dispatch function from context
    const dispatch = useContext(FormDispatch);

    // Define functions for validating each field, stating which fields need
    // to be sent and checked
    const validateBuying = () => {
        dispatch({ type: actionTypes.validate, validationInput: inputs.buying })
    };

    const validateSelling = () => {
        dispatch({ type: actionTypes.validate, validationInput: inputs.selling })
    };

    const validateProduct = () => {
        dispatch({ type: actionTypes.validate, validationInput: inputs.product })
    };

    // Only let them progress if all fields are non-empty and there are no
    // corrections left
    // TODO: Make sure this "no corrections left" condition doesn't break stuff
    // when they pick a correction.
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
                <SubFormTitle>Step 4 of 4: Final Check</SubFormTitle>
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
