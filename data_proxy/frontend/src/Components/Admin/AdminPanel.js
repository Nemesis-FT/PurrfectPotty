import React, {useEffect, useState} from 'react';
import {Heading, Chapter, Box, Form, Button, Panel} from "@steffo/bluelib-react";
import schema from "../../config";
import {useAppContext} from "../../Context";
import Settings from "./Settings";

export default function AdminPanel() {
    const [settings, setSettings] = useState(null)
    const {address} = useAppContext()
    const {token} = useAppContext()
    const [id, setId] = useState("")

    useEffect(() => {
        if(address){
            getSettings()
        }

    }, [address])

    async function getSettings() {
        let response = await fetch(schema + address + "/api/settings/v1/", {
            method: "GET",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': "Bearer " + token,
            },
        });
        if (response.status === 200) {
            let values = await response.json()
            setSettings(values)
        }
    }


    return (
        <div style={{minWidth: "unset"}}>
            <Panel>
                <Heading level={3}>Settings panel</Heading>
                {settings ? (
                    <Settings settings={settings}/>
                ) : (
                    <p> Caricamento... </p>
                )}
            </Panel>
        </div>
    );
}