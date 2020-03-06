/* jshint esversion: 9 */

import React, { useReducer, useEffect } from 'react';
import { Grid, Paper, CircularProgress, InputAdornment, Typography } from '@material-ui/core';
import CssBaseline from '@material-ui/core/CssBaseline';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import { subForms, initialFormState, actionTypes, inputs, reducer, FormDispatch, useStyles, all_zeroes, int_re, decimal_re, date_format_re, host } from './form-constants';
import { FormFieldWrapper, SubmitField, SubmitButton, NextButton, PrevButton, SubFormTitle, CurrencyField } from './form-components';
import AutorenewRoundedIcon from '@material-ui/icons/AutorenewRounded';

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
        
        switch (input) {
            case inputs.buying:
                // Validate buying party via API
                // curl --request POST --data '{"name": "Axon"}' localhost:8000/api/validate/company/
                console.log("Currently validating buying party: ", state.buyingParty);
                fetch(host + 'api/validate/company/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        "name": state.buyingParty,
                        "fieldType": "buyingParty"
                    }),
                })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Network response not ok!");
                    }
                    return response.json();
                })
                .then((data) => {
                    console.log('Success:', data);
                    if (data.success === false) {

                        if (data.autoCorrect === true) {
                            dispatch({
                                type: actionTypes.new,
                                input: inputs.buying,
                                newValue: data.names[0]
                            });
                        } else {
                            let suggestions = data.names;
                            // If suggestions available, pass them to form
                            if (suggestions.length > 0) {
                                dispatch({
                                    type: actionTypes.markCorrect,
                                    input: inputs.buying
                                });
                                dispatch({
                                    type: actionTypes.provideSuggestions,
                                    input: inputs.buying,
                                    suggestions: suggestions
                                });
                            } else {  // No suggestions - just mark as incorrect
                                dispatch({
                                    type: actionTypes.markNoSuggestions,
                                    input: inputs.buying
                                });
                            }
                        }

                    }
                    dispatch({ type: actionTypes.markRequestComplete, input: inputs.buying });
                })
                .catch((error) => {
                    console.error('Error:', error);
                    dispatch({ type: actionTypes.markRequestComplete, input: inputs.buying });
                });
                
                break;

            case inputs.selling:
                // Validate selling party using API

                console.log("Currently validating selling party: ", state.sellingParty);
                fetch(host + 'api/validate/company/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        "name": state.sellingParty,
                        "fieldType": "sellingParty"
                    }),
                })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Network response not ok!");
                    }
                    return response.json();
                })
                .then((data) => {
                    console.log('Success:', data);
                    if (data.success === false) {

                        if (data.autoCorrect === true) {
                            dispatch({
                                type: actionTypes.new,
                                input: inputs.selling,
                                newValue: data.names[0]
                            });
                        } else {
                            let suggestions = data.names;
                            // If suggestions available, pass them to form
                            if (suggestions.length > 0) {
                                dispatch({
                                    type: actionTypes.markCorrect,
                                    input: inputs.selling
                                });
                                dispatch({
                                    type: actionTypes.provideSuggestions,
                                    input: inputs.selling,
                                    suggestions: suggestions
                                });
                            } else {  // No suggestions - mark as such
                                dispatch({
                                    type: actionTypes.markNoSuggestions,
                                    input: inputs.selling
                                });
                            }
                        }
                    }

                    dispatch({ type: actionTypes.markRequestComplete, input: inputs.selling });
                })
                .catch((error) => {
                    console.error('Error:', error);
                    dispatch({ type: actionTypes.markRequestComplete, input: inputs.selling });
                });
                break;

            case inputs.product:

                console.log("Currently validating product: ", state.productName);
                fetch(host + 'api/validate/product/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        "product": state.productName,
                        "sellingParty": state.sellingParty,
                        "buyingParty": state.buyingParty
                    }),
                })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error("Network response not ok!");
                    }
                    return response.json();
                })
                .then((data) => {
                    console.log('Success: ', data);
                    if (data.success === false) {

                        if (data.canSwap === true) {
                            console.log("Swapping buying and selling parties.");
                            let buying = state.buyingParty;
                            let selling = state.sellingParty;
                            dispatch({
                                type: actionTypes.new,
                                input: inputs.buying,
                                newValue: selling
                            });
                            dispatch({
                                type: actionTypes.new,
                                input: inputs.selling,
                                newValue: buying
                            });
                        } else {
                            let wrongSelling = data.sellingParty !== state.sellingParty;
                            // let wrongBuying = data.buyingParty === false;

                            if (wrongSelling) {
                                // TODO: Maybe correct automatically rather than suggesting??
                                dispatch({
                                    type: actionTypes.markCorrect,
                                    input: inputs.selling
                                });
                                dispatch({
                                    type: actionTypes.provideSuggestions,
                                    input: inputs.selling,
                                    suggestions: [data.sellingParty]
                                });
                            }
                            // if (wrongBuying) {
                            //     dispatch({
                            //         type: actionTypes.markNoSuggestions,
                            //         input: inputs.buying
                            //     });
                            // }
                            if (data.product === false) {
                                let suggestions = [];
                                if ("products" in data) {
                                    suggestions = data.products;
                                }
                                // If suggestions available, pass them to form
                                if (suggestions.length > 0) {
                                    dispatch({
                                        type: actionTypes.markCorrect,
                                        input: inputs.product
                                    });
                                    dispatch({
                                        type: actionTypes.provideSuggestions,
                                        input: inputs.product,
                                        suggestions: suggestions
                                    });
                                } else {  // No suggestions - mark as such
                                    dispatch({
                                        type: actionTypes.markNoSuggestions,
                                        input: inputs.product
                                    });
                                }
                            }
                        }

                    }
                    dispatch({ type: actionTypes.markRequestComplete, input: inputs.product });
                })
                .catch((error) => {
                    console.error('Error:', error);
                    dispatch({ type: actionTypes.markRequestComplete, input: inputs.product });
                });
                break;

            case inputs.uPrice:
                // Check if price entered is a positive price
                if (all_zeroes.test(state.underlyingPrice) === true) {
                    dispatch({
                        type: actionTypes.markNoSuggestions,
                        input: inputs.uPrice
                    });

                } else if (decimal_re.test(state.underlyingPrice) !== true) {
                    dispatch({
                        type: actionTypes.markNoSuggestions,
                        input: inputs.uPrice
                    });

                } else {
                    // TODO: Validate with API!
                    dispatch({
                        type: actionTypes.markCorrect,
                        input: inputs.uPrice
                    });
                }

                dispatch({ type: actionTypes.markRequestComplete, input: inputs.uPrice });
                break;
            
            case inputs.mDate:
                if (date_format_re.test(state.maturityDate) !== true) {
                    dispatch({
                        type: actionTypes.markNoSuggestions,
                        input: inputs.mDate
                    });
                } else {
                    console.log("Validating maturity date: ", state.maturityDate)
                    fetch(host + 'api/validate/maturitydate/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            "date": state.maturityDate
                        }),
                    })
                    .then((response) => {
                        if (!response.ok) {
                            throw new Error("Network response not ok!");
                        }
                        return response.json();
                    })
                    .then((data) => {
                        if (data.success === true) {
                            dispatch({
                                type: actionTypes.markCorrect,
                                input: inputs.mDate
                            });
                        } else {
                            dispatch({
                                type: actionTypes.markNoSuggestions,
                                input: inputs.mDate
                            });
                        }
                    })
                    .catch((error) => {
                        console.error('Error:', error);
                    });
                }

                dispatch({ type: actionTypes.markRequestComplete, input: inputs.mDate });
                break;
            
            case inputs.quantity:
                // Check that input quantity is a positive integer, consisting
                // of only digit characters.
                if (all_zeroes.test(state.quantity) === true) {
                    dispatch({
                        type: actionTypes.markNoSuggestions,
                        input: inputs.quantity
                    });
                } else if (int_re.test(state.quantity) !== true) {
                    dispatch({
                        type: actionTypes.markNoSuggestions,
                        input: inputs.quantity
                    });
                } else {
                    // TODO: Validate with API!
                    dispatch({
                        type: actionTypes.markCorrect,
                        input: inputs.quantity
                    });
                }

                dispatch({ type: actionTypes.markRequestComplete, input: inputs.quantity });
                break;

            case inputs.sPrice:
                // Check if price entered is a number
                if (all_zeroes.test(state.strikePrice) === true) {
                    dispatch({
                        type: actionTypes.markNoSuggestions,
                        input: inputs.sPrice
                    });

                } else if (decimal_re.test(state.strikePrice) !== true) {
                    dispatch({
                        type: actionTypes.markNoSuggestions,
                        input: inputs.sPrice
                    });

                } else {
                    // TODO: Validate with API!
                    dispatch({
                        type: actionTypes.markCorrect,
                        input: inputs.sPrice
                    });
                }

                dispatch({ type: actionTypes.markRequestComplete, input: inputs.sPrice });
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
        // If there are corrections to be logged
        if (log.length > 0) {
            const [field, oldVal, newVal] = log[log.length - 1];
            console.log("Sending correction: " + field + " " + oldVal + " " + newVal);

            fetch(host + 'api/corrections/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "field": field,
                    "oldValue": oldVal,
                    "newValue": newVal
                }),
            });

        }
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
            elem = (
                <Paper elevation={3} className={classes.formContainer}>
                    <FormDispatch.Provider value={dispatch}>
                        <SubFormThree fields={{...state}} />
                    </FormDispatch.Provider>
                </Paper>
            );
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
    let canEnterProduct = (
        props.fields.correctionFields[inputs.buying].length > 0
        || props.fields.correctionFields[inputs.selling].length > 0
        || props.fields.incorrectFields[inputs.buying]
        || props.fields.incorrectFields[inputs.selling]
        || props.fields.requestingFields[inputs.buying]
        || props.fields.requestingFields[inputs.selling]
        || props.fields.sellingParty === ""
        || props.fields.buyingParty === ""
    );
    let anyEmptyOrError = (
        canEnterProduct
        || props.fields.correctionFields[inputs.product].length > 0
        || props.fields.incorrectFields[inputs.product]
        || props.fields.requestingFields[inputs.product]
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
                disabled={props.fields.requestingFields[inputs.buying]}
                helperText="Please enter the buying party."
                errorMessage="This input is not a valid company; Please try again."
                suggestionMessage="This input looks wrong; Click here to see suggestions."
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormFieldWrapper
                id={inputs.selling}
                label="Selling Party"
                value={props.fields.sellingParty}
                suggestions={props.fields.correctionFields[inputs.selling]}
                incorrectField={props.fields.incorrectFields[inputs.selling]}
                disabled={props.fields.requestingFields[inputs.selling]}
                helperText="Please enter the selling party."
                errorMessage="This input is not a valid company; Please try again."
                suggestionMessage="This input looks wrong; Click here to see suggestions."
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <FormFieldWrapper
                id={inputs.product}
                label="Product Name"
                value={props.fields.productName}
                suggestions={props.fields.correctionFields[inputs.product]}
                incorrectField={props.fields.incorrectFields[inputs.product]}
                disabled={props.fields.requestingFields[inputs.product]}
                helperText="Please enter the product name."
                errorMessage="This input is not a valid product; Please try again."
                suggestionMessage="This input looks wrong; Click here to see suggestions."
                disabled={canEnterProduct}
            />
        </Grid>
        <Grid item className={classes.formItemContainer}>
            <NextButton disabled={anyEmptyOrError}/>
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
        || props.fields.correctionFields[inputs.nCurr].length > 0
        || props.fields.correctionFields[inputs.mDate].length > 0
        || props.fields.incorrectFields[inputs.uCurr]
        || props.fields.incorrectFields[inputs.nCurr]
        || props.fields.incorrectFields[inputs.mDate]
        || props.fields.requestingFields[inputs.uCurr]
        || props.fields.requestingFields[inputs.nCurr]
        || props.fields.requestingFields[inputs.mDate]
        || props.fields.underlyingCurrency === ""
        || props.fields.notionalCurrency === ""
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
                <CurrencyField
                    id={inputs.nCurr}
                    label="Notional Currency"
                    value={props.fields.notionalCurrency}
                    suggestions={props.fields.correctionFields[inputs.nCurr]}
                    currencies={props.fields.currencies}
                />
            </Grid>
            <Grid item className={classes.formItemContainer}>
                <FormFieldWrapper
                    id={inputs.mDate}
                    label="Maturity Date"
                    value={props.fields.maturityDate}
                    suggestions={props.fields.correctionFields[inputs.mDate]}
                    incorrectField={props.fields.incorrectFields[inputs.mDate]}
                    disabled={props.fields.requestingFields[inputs.mDate]}
                    helperText="Please enter the maturity date, in dd/mm/yyyy format."
                    errorMessage="This must be a valid, future date; Please try again."
                />
            </Grid>
            <Grid item className={classes.formItemContainer}>
                <PrevButton />
                <NextButton disabled={anyEmptyOrError}/>
            </Grid>
        </Grid>
        );
}


function SubFormThree(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Only let them progress if all fields are non-empty and there are no
    // corrections left
    let anyEmptyOrError = (
        props.fields.correctionFields[inputs.quantity].length > 0
        || props.fields.correctionFields[inputs.uPrice].length > 0
        || props.fields.correctionFields[inputs.sPrice].length > 0
        || props.fields.incorrectFields[inputs.quantity]
        || props.fields.incorrectFields[inputs.uPrice]
        || props.fields.incorrectFields[inputs.sPrice]
        || props.fields.requestingFields[inputs.quantity]
        || props.fields.requestingFields[inputs.uPrice]
        || props.fields.requestingFields[inputs.sPrice]
        || props.fields.quantity === ""
        || props.fields.underlyingPrice === ""
        || props.fields.strikePrice === ""
        
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
                <SubFormTitle>Step 3 of 4</SubFormTitle>
            </Grid>
            <Grid item className={classes.formItemContainer}>
                <FormFieldWrapper
                    id={inputs.uPrice}
                    label="Underlying Price"
                    value={props.fields.underlyingPrice}
                    suggestions={props.fields.correctionFields[inputs.uPrice]}
                    incorrectField={props.fields.incorrectFields[inputs.uPrice]}
                    disabled={props.fields.requestingFields[inputs.uPrice]}
                    helperText={"Please enter the underlying price, in: " + props.fields.underlyingCurrency}
                    errorMessage="This input must be a positive, valid price; Please try again."
                />
            </Grid>
            <Grid item className={classes.formItemContainer}>
                <FormFieldWrapper
                    id={inputs.sPrice}
                    label="Strike Price"
                    value={props.fields.strikePrice}
                    suggestions={props.fields.correctionFields[inputs.sPrice]}
                    incorrectField={props.fields.incorrectFields[inputs.sPrice]}
                    disabled={props.fields.requestingFields[inputs.sPrice]}
                    helperText={"Please enter the strike price, in: " + props.fields.underlyingCurrency}
                    errorMessage="This input must be a positive, valid price; Please try again."
                />
            </Grid>
            <Grid item className={classes.formItemContainer}>
                <FormFieldWrapper
                    id={inputs.quantity}
                    label="Quantity"
                    value={props.fields.quantity}
                    suggestions={props.fields.correctionFields[inputs.quantity]}
                    incorrectField={props.fields.incorrectFields[inputs.quantity]}
                    disabled={props.fields.requestingFields[inputs.quantity]}
                    helperText="Please enter the quantity of products sold."
                    errorMessage="This input must be a positive integer; Please try again."
                />
            </Grid>
            
            <Grid item className={classes.formItemContainer}>
                <PrevButton />
                <NextButton disabled={anyEmptyOrError}/>
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
                <Typography gutterBottom={true} variant="body1">
                    {"Buying Party: " + props.fields.buyingParty}
                </Typography>
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <Typography gutterBottom={true} variant="body1">
                    {"Selling Party: " + props.fields.sellingParty}
                </Typography>
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <Typography gutterBottom={true} variant="body1">
                    {"Product Name: " + props.fields.productName}
                </Typography>
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <Typography gutterBottom={true} variant="body1">
                    {"Product Quantity: " + props.fields.quantity}
                </Typography>
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <Typography gutterBottom={true} variant="body1">
                    {"Underlying Price: " + props.fields.underlyingPrice}
                </Typography>
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <Typography gutterBottom={true} variant="body1">
                    {"Underlying Currency: " + props.fields.underlyingCurrency}
                </Typography>
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <Typography gutterBottom={true} variant="body1">
                    {"Maturity Date: " + props.fields.maturityDate}
                </Typography>
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <Typography gutterBottom={true} variant="body1">
                    {"Notional Currency: " + props.fields.notionalCurrency}
                </Typography>
            </Grid>
            <Grid item className={classes.submitItemContainer}>
                <Typography gutterBottom={true} variant="body1">
                    {"Strike Price: " + props.fields.strikePrice}
                </Typography>
            </Grid>
            <Grid item className={classes.submitButton}>
                <PrevButton />
                <SubmitButton disabled={anyInputEmpty} />
            </Grid>
        </Grid>
    );
}
