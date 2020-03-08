/* jshint esversion: 9 */

import React, { useContext, useEffect } from 'react';
import { Typography, Select } from '@material-ui/core';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';
import IconButton from '@material-ui/core/IconButton';
import NavigateNextIcon from '@material-ui/icons/NavigateNext';
import ErrorOutlineIcon from '@material-ui/icons/ErrorOutline';
import NavigateBeforeIcon from '@material-ui/icons/NavigateBefore';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import Menu from '@material-ui/core/Menu';
import MenuItem from '@material-ui/core/MenuItem';
import InputLabel from '@material-ui/core/InputLabel';
import { actionTypes, FormDispatch, useStyles, inputs, host } from './form-constants';

export { FormFieldWrapper, SubmitButton, NextButton, PrevButton, IgnoreButton, SubFormTitle, CurrencyField };


// Component for text fields in the form
function FormField(props) {
    // Get dispatch function from the reducer hook via a context hook
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


function CurrencyField(props) {
    // Get dispatch function from the reducer hook via a context hook
    const dispatch = useContext(FormDispatch);

    const [open, setOpen] = React.useState(false);

    const handleClose = () => {
        setOpen(false);
    };

    const handleOpen = () => {
        setOpen(true);
    };

    // Function for handling changes
    const handleChange = e => {
        dispatch({
            input: props.id,
            type: actionTypes.new,
            newValue: e.target.value
        });
        dispatch({ type: actionTypes.validate, validationInput: props.id });
    };

    // Fetch valid currencies for the day!
    useEffect(() => {
        if (props.currencies.length === 0) {
            // Fetch list of valid currencies for today from API!
            fetch(host + 'api/currencies/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then((response) => {
                if (!response.ok) {
                    throw new Error("Network response not ok!");
                }
                return response.json();
            })
            .then((data) => {
                dispatch({
                    type: actionTypes.populateCurrencies,
                    currencies: data.currencies
                });

                // Default currencies to USD
                dispatch({
                    type: actionTypes.new,
                    input: inputs.uCurr,
                    newValue: "USD"
                });
                dispatch({
                    type: actionTypes.new,
                    input: inputs.nCurr,
                    newValue: "USD"
                });
            })
            .catch((error) => {
                console.error('Error:', error);
            });
        }
    }, []);  // Will only run when the component mounts!

    const currencyComponents = props.currencies.map((curr, i) =>
        <MenuItem key={i} value={curr}>{curr}</MenuItem>
    );

    return (<>
        <InputLabel id="select-label">{props.label}</InputLabel>
        <Select
            labelId="select-label"
            open={open}
            onClose={handleClose}
            onOpen={handleOpen}
            onChange={handleChange}
            {...props}
        >
            {currencyComponents}
        </Select>
    </>);
}


function ErrorNoSuggestions(props) {
    // Ignore incorrectField prop on child elements
    const { incorrectField, ...formProps } = props;

    return <FormField error {...formProps}/>;
}


// Component for text fields that need correction in the form, where
// suggestions are provided.
function ErrorWithSuggestions(props) {
    // Set the anchor element on the menu
    const [anchor, setAnchor] = React.useState(null);

    // Get dispatch function from the reducer hook via a context hook
    const dispatch = useContext(FormDispatch);

    // Functions for setting the menu anchor to the current form field
    const whenFocused = event => setAnchor(event.currentTarget);

    const whenLeaving = val => () => {
        // If there is a correction string, then correct the value!
        if (val !== null) {
            dispatch({
                input: props.id,
                type: actionTypes.correction,
                oldValue: props.value,
                newValue: val
            });

            // If a product suggestion has been picked, mark it for re-validation
            if (props.id === inputs.product) {
                dispatch({ type: actionTypes.markRequesting, input: props.id });
                dispatch({ type: actionTypes.validate, validationInput: props.id }); 
            }
        }
        
        setAnchor(null); // Make menu go away
    };

    // Make suggestions React components
    const suggestions = props.suggestions.map((s, i) =>
        <MenuItem onClick={whenLeaving(s)} key={i}>{s}</MenuItem>
    );

    return (
    <>
        <FormField error aria-controls="simple-menu" aria-haspopup="true" onClick={whenFocused} {...props}/>
        <Menu
            id="simple-menu"
            anchorEl={anchor}
            keepMounted
            open={Boolean(anchor)}
            onClose={whenLeaving}
        >
            <MenuItem disabled={true}>Please select a correction:</MenuItem>
            {suggestions}
            <MenuItem onClick={whenLeaving(props.value)}>Stick with: {props.value}</MenuItem>
        </Menu>
    </>);
}


function FormFieldWrapper(props) {
    // Fetch dispatch function from context
    const dispatch = useContext(FormDispatch);

    // Define functions for validating each field, stating which fields need
    // to be sent and checked
    const validate = () => {
        dispatch({ type: actionTypes.markRequesting, input: props.id });
        dispatch({ type: actionTypes.validate, validationInput: props.id });
    };

    // Ignore incorrectField prop on child elements
    const { incorrectField, errorMessage, suggestionMessage, ...inputProps } = props;

    // If field is marked as incorrect
    if (props.incorrectField === true) {
        return (
            <ErrorNoSuggestions
                { ...inputProps }
                incorrectField={props.incorrectField}
                onBlur={validate}
                helperText={props.errorMessage}  // Needs to go after props!
            />
        );

    // If field has no suggestions
    } else if (props.suggestions.length === 0) {
        return (
            <FormField
                { ...inputProps }
                onBlur={validate}
            />
        );

    // Otherwise, return an error field
    } else {
        return (
            <ErrorWithSuggestions
                { ...inputProps }
                onBlur={validate}
                helperText={props.suggestionMessage}  // Needs to go after props!
            />
        );    
    }
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


function PrevButton(props) {
    // Fetch dispatch function from context
    const dispatch = useContext(FormDispatch);

    // Event function to get the SuperForm to render the previous SubForm
    const goToPrevForm = () => dispatch({ type: actionTypes.prevForm });

    return (
        <IconButton
            // className={classes.button}
            onClick={goToPrevForm}
            aria-label="previous"
            {...props}
        >
            <NavigateBeforeIcon />
        </IconButton>
    );
}

function IgnoreButton(props) {
    // Fetch defined styling
    const classes = useStyles(props);

    // Fetch dispatch function from context
    const dispatch = useContext(FormDispatch);

    // Event function to get the SuperForm to render the next SubForm
    const goToNextForm = () => dispatch({ type: actionTypes.nextForm });

    return (
        <Button
            variant="contained"
            color="secondary"
            className={classes.button}
            endIcon={<ErrorOutlineIcon />}
            onClick={goToNextForm}
            {...props}
        >
            Ignore Errors
        </Button>
    );
}


function SubmitButton(props) {
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
            endIcon={<CloudUploadIcon />}
            onClick={goToNextForm}
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