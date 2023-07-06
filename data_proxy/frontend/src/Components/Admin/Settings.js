import React, {useEffect, useState} from 'react';
import {Heading, Chapter, Box, Form, Button, Panel} from "@steffo/bluelib-react";
import schema from "../../config";
import {useAppContext} from "../../Context";

export default function Settings(props) {
    const [sr, setSr] = useState(props.settings.sampling_rate)
    const [uc, setUc] = useState(props.settings.use_counter)
    const [usc, setUsc] = useState(props.settings.used_offset)
    const [tt, setTt] = useState(props.settings.tare_timeout)
    const [dt, setDt] = useState(props.settings.danger_threshold)
    const [dc, setDc] = useState(props.settings.danger_counter)
    const {address} = useAppContext()
    const {token} = useAppContext()

    async function submit() {
        let response = await fetch(schema + address + "/api/settings/v1/", {
            method: "PUT",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': "Bearer " + token,
                'Access-Control-Allow-Origin': process.env.DOMAIN,

            },
            body: JSON.stringify({
                sampling_rate: sr,
                use_counter: uc,
                used_offset: usc,
                tare_timeout: tt,
                danger_threshold: dt,
                danger_counter: dc
            })
        });
        if (response.status === 200) {
            let values = await response.json()
            alert("Update successful!")
        } else {
            alert("Something went wrong.")
        }
    }


    return (
        <div style={{minWidth: "unset"}}>
                <Chapter>
                    <Form.Row>
                        <Form.Field onSimpleChange={e => setSr(e)} value={sr} required={true}
                                    label={"Sampling rate (ms)"}>
                        </Form.Field>
                        <Form.Field onSimpleChange={e => setUc(e)} value={uc} required={true}
                                    label={"Use counter"}>
                        </Form.Field>
                    </Form.Row>
                    <Form.Row>
                        <Form.Field onSimpleChange={e => setUsc(e)} value={usc} required={true}
                                    label={"Used offset"}>
                        </Form.Field>
                        <Form.Field onSimpleChange={e => setTt(e)} value={tt}
                                    required={true}
                                    label={"Tare timeout (ms)"}>
                        </Form.Field>
                    </Form.Row>
                    <Form.Row>
                        <Form.Field onSimpleChange={e => setDt(e)} value={dt} required={true}
                                    label={"Danger threshold (kg)"}>
                        </Form.Field>
                        <Form.Field onSimpleChange={e => setDc(e)} value={dc}
                                    required={true}
                                    label={"Danger counter"}>
                        </Form.Field>
                    </Form.Row>
                </Chapter>

            <Chapter>
                <Button children={"Save"} onClick={e => submit()}/>
            </Chapter>
        </div>
    );
}