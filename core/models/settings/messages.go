package settings

import "gorm.io/gorm"

type Message struct {
	gorm.Model
	Name       string
	Value      string
	SettingsID uint
}

const (
	MESSAGE_MissingField           string = "MissingField"
	MESSAGE_TargetNotAllowed       string = "TargetNotAllowed"
	MESSAGE_FeatureNotEnabled      string = "FeatureNotEnabled"
	MESSAGE_InvalidInput           string = "InvalidInput"
	MESSAGE_InvalidField           string = "InvalidField"
	MESSAGE_UnknownError           string = "UnknownError"
	MESSAGE_RequestTimeout         string = "RequestTimeout"
	MESSAGE_ConnectionError        string = "ConnectionError"
	MESSAGE_AuthenticationError    string = "AuthenticationError"
	MESSAGE_ResponseParsingFailure string = "ResponseParsingFailure"
	MESSAGE_EmptyResponse          string = "EmptyResponse"
)

var DefaultMessages map[string]string = map[string]string{
	MESSAGE_MissingField:           "{.Value} must be specified.",
	MESSAGE_TargetNotAllowed:       "{.Value} is not allowed.",
	MESSAGE_FeatureNotEnabled:      "{.Value} is not enabled.",
	MESSAGE_InvalidInput:           "{.Value} is invalid.",
	MESSAGE_InvalidField:           "{.Value} is an invalid {.Type}",
	MESSAGE_UnknownError:           "Something went wrong.",
	MESSAGE_RequestTimeout:         "Request timed out.",
	MESSAGE_ConnectionError:        "Error connecting to {.Value}: {.Error}",
	MESSAGE_AuthenticationError:    "Error authenticating to {.Value}: {.Error}",
	MESSAGE_ResponseParsingFailure: "Error reading response.",
	MESSAGE_EmptyResponse:          "The query completed, but no results were found.",
}

func SeedMessages() (messages []Message) {
	for n, v := range DefaultMessages {
		msg := Message{
			Name:  n,
			Value: v,
		}
		messages = append(messages, msg)
	}
	return
}
