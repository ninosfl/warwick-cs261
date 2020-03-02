/* jshint esversion: 9 */

import React, { useReducer, useEffect } from 'react';
import { Grid, Paper, CircularProgress } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import { subForms, initialFormState, actionTypes, inputs, reducer, FormDispatch, useStyles } from './form-constants';
import { FormFieldWrapper, SubmitField, SubmitButton, NextButton, SubFormTitle, CurrencyField } from './form-components';

export { SuperForm };


// Form component for holding overall form data
function SuperForm(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Use reducer hook to handle form data
    const [state, dispatch] = useReducer(reducer, initialFormState);

    // Use effect hook for api validation
    // No need to reset validationInputs to some default value, since this
    // effect will only run when it changes.
    useEffect(() => {
        let input = null;
        if (state.validationInputs.length > 0) {
            input = state.validationInputs[state.validationInputs.length - 1];
        }
        
        // TODO: Make this do mad fetching to get validated values
        switch (input) {
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

                break;

            case inputs.uPrice:
                // Check if price entered is a number
                if (isNaN(state.underlyingPrice)) {
                    dispatch({
                        type: actionTypes.markIncorrect,
                        input: inputs.uPrice
                    });

                } else {
                    // TODO: Validate with API!
                    dispatch({
                        type: actionTypes.markCorrect,
                        input: inputs.uPrice
                    });
                }

                break;
            
            case inputs.mDate:
                const date_format_re = /^\d{2}\/\d{2}\/\d{4}$/;
                if (date_format_re.test(state.maturityDate) !== true) {
                    dispatch({
                        type: actionTypes.markIncorrect,
                        input: inputs.mDate
                    });
                } else {
                    dispatch({
                        type: actionTypes.markCorrect,
                        input: inputs.mDate
                    });
                }

                break;
            
            case inputs.quantity:
                // Check that input quantity is an integer, consisting of
                // only digit characters.
                const int_re = /^\d+$/;
                if (int_re.text(state.quantity) !== true) {
                    dispatch({
                        type: actionTypes.markIncorrect,
                        input: inputs.quantity
                    });
                } else {
                    // TODO: Validate with API!
                    dispatch({
                        type: actionTypes.markCorrect,
                        input: inputs.quantity
                    });
                }

                break;

            case inputs.sPrice:
                // Check if price entered is a number
                if (isNaN(state.underlyingPrice)) {
                    dispatch({
                        type: actionTypes.markIncorrect,
                        input: inputs.uPrice
                    });

                } else {
                    // TODO: Validate with API!
                    dispatch({
                        type: actionTypes.markCorrect,
                        input: inputs.uPrice
                    });
                }

                break;

            // TODO: Below validations!

            case inputs.uCurr:
                break;
            
            case inputs.nCurr:
                break;

            default:
                break;
        }
    }, [state.validationInputs]);  // Only perform effect when validationInputs changes

    // Use effect hook for logging corrections!
    useEffect(() => {
        const log = state.correctionFields.correctionLog;
        if (log.length > 0) {
            const [field, oldVal, newVal] = log[log.length - 1];
        }
        // TODO: Send fields to API!
    }, [state.correctionFields.correctionLog]);  // Only perform effect when correctionFields changes

    // Use effect hook for submitting form
    useEffect(() => {
        // TODO: Get this to actually do some submitting you muppet
        if (state.submitNow) {
            document.write("Submitted! (Obviously not this is debug text)");
        }
    }, [state.submitNow]);

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
            elem = (
                <Paper elevation={3} className={classes.formContainer}>
                    <FormDispatch.Provider value={dispatch}>
                        <SubFormTwo fields={{...state}} />
                    </FormDispatch.Provider>
                </Paper>
            );
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

    // Only let them progress if all fields are non-empty and there are no
    // corrections left
    let anyEmptyOrError = (
        props.fields.correctionFields[inputs.buying].length > 0
        || props.fields.correctionFields[inputs.selling].length > 0
        || props.fields.correctionFields[inputs.product].length > 0
        || props.fields.incorrectFields[inputs.buying]
        || props.fields.incorrectFields[inputs.selling]
        || props.fields.incorrectFields[inputs.product]
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
                suggestions={props.fields.correctionFields[inputs.buying]}
                incorrectField={props.fields.incorrectFields[inputs.buying]}
                helperText="Please enter the buying party."
                errorMessage="This input looks wrong; Click here to see suggestions."
            />
        </Grid>
        <Grid item container direction="row" alignItems="center" className={classes.formItemContainer}>
            <Grid item xs={10}><FormFieldWrapper
                id={inputs.selling}
                label="Selling Party"
                value={props.fields.sellingParty}
                suggestions={props.fields.correctionFields[inputs.selling]}
                incorrectField={props.fields.incorrectFields[inputs.selling]}
                helperText="Please enter the selling party."
                errorMessage="This input looks wrong; Click here to see suggestions."
                disabled={props.fields.validatingFields[inputs.selling]}
            /></Grid>
            <Grid item>{props.fields.validatingFields[inputs.selling] && <CircularProgress size={30}/>}</Grid>
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormFieldWrapper
                id={inputs.product}
                label="Product Name"
                value={props.fields.productName}
                suggestions={props.fields.correctionFields[inputs.product]}
                incorrectField={props.fields.incorrectFields[inputs.product]}
                helperText="Please enter the product name."
                errorMessage="This input looks wrong; Click here to see suggestions."
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            {anyEmptyOrError ? <NextButton disabled /> : <NextButton />}
        </Grid>
    </Grid>
    );
}


function SubFormTwo(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Only let them progress if all fields are non-empty and there are no
    // corrections left
    let anyEmptyOrError = (
        props.fields.correctionFields[inputs.uCurr].length > 0
        || props.fields.correctionFields[inputs.uPrice].length > 0
        || props.fields.correctionFields[inputs.mDate].length > 0
        || props.fields.incorrectFields[inputs.uCurr]
        || props.fields.incorrectFields[inputs.uPrice]
        || props.fields.incorrectFields[inputs.mDate]
        || props.fields.underlyingCurrency === ""
        || props.fields.underlyingPrice === ""
        || props.fields.maturityDate === ""
        
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
                <SubFormTitle>Step 2 of 4</SubFormTitle>
            </Grid>
            <Grid item className={classes.formItemContainer}>
                <CurrencyField
                    id={inputs.uCurr}
                    label="Underlying Currency"
                    value={props.fields.underlyingCurrency}
                    suggestions={props.fields.correctionFields[inputs.uCurr]}
                    currencies={props.fields.currencies}
                />
            </Grid>
            <Grid item className={classes.formItemContainer}>
                <FormFieldWrapper
                    id={inputs.uPrice}
                    label="Underlying Price"
                    value={props.fields.underlyingPrice}
                    suggestions={props.fields.correctionFields[inputs.uPrice]}
                    incorrectField={props.fields.incorrectFields[inputs.uPrice]}
                    helperText="Please enter the underlying price, in the currency above."
                    errorMessage="This input must be a number; Please try again."
                />
            </Grid>
            <Grid item className={classes.formItemContainer}>
                <FormFieldWrapper
                    id={inputs.mDate}
                    label="Maturity Date"
                    value={props.fields.maturityDate}
                    suggestions={props.fields.correctionFields[inputs.mDate]}
                    incorrectField={props.fields.incorrectFields[inputs.mDate]}
                    helperText="Please enter the maturity date, in dd/mm/yyyy format."
                    errorMessage="This input must be in dd/mm/yyyy format; Please try again."
                />
            </Grid>
            <Grid item className={classes.formItemContainer}>
                {anyEmptyOrError ? <NextButton disabled /> : <NextButton />}
            </Grid>
        </Grid>
        );
}


// Subform for the final Submit page, where the user checks everything
function SubmitForm(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // If any fields are blank, you can't submit!
    const fields = Object.values(inputs).map(input => props.fields[input]);
    let anyInputEmpty = fields.some(field => field === "");

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
            {anyInputEmpty ? <SubmitButton disabled/> : <SubmitButton/>}
            </Grid>
        </Grid>
    );
}

/* FOR PROGRESS INDICATORS WHILE MAKING API REQUESTS
<Grid container direction="row">
    <FormFieldWrapper
        id={inputs.uPrice}
        label="Underlying Price"
        value={props.fields.underlyingPrice}
        suggestions={props.fields.correctionFields[inputs.uPrice]}
        incorrectField={props.fields.incorrectFields[inputs.uPrice]}
        helperText="Please enter the underlying price, in the currency above."
        errorMessage="This input must be a number; Please try again."
        disabled={props.fields.requestingFields[inputs.uPrice]}
    />
    {props.fields.requestingFields[inputs.uPrice] && <CircularProgress />}
</Grid>
*/
