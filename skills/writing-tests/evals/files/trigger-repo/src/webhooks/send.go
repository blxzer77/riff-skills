package webhooks

import (
	"bytes"
	"net/http"
)

// Send posts the payload to the subscriber URL once.
func Send(client *http.Client, url string, payload []byte) error {
	resp, err := client.Post(url, "application/json", bytes.NewReader(payload))
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	return nil
}
