import React, {useEffect, useState} from "react"
import {useNavigate} from "react-router-dom";
import {useAppContext} from "../Context";
import schema from "../config";
import {Heading, Panel, Form, Button, Chapter} from "@steffo/bluelib-react";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const {token, setToken} = useAppContext()
    const {address, setAddress} = useAppContext()

    const navigate = useNavigate()

    useEffect( () => {
        console.debug(address)
        if (localStorage.getItem("address") && address == null) {
            let address = localStorage.getItem("address")
            console.debug(address)
            setAddress(address)
        }
    })

    async function login() {
        let body = {
            "grant_type":"password",
            "username":email,
            "password":password

        }
        var formB = []
        for (var property in body) {
            var encodedKey = encodeURIComponent(property);
            var encodedValue = encodeURIComponent(body[property]);
            formB.push(encodedKey + "=" + encodedValue);
        }
        formB = formB.join("&");

        const response = await fetch(schema+address+"/token", {
            method: "POST",
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            },
            body: formB
        });
        if (response.status === 200) {
            let values = await response.json()
            console.debug(values)
            setToken(values.access_token)
            navigate("/dashboard")
        }
        else{
            alert("Credenziali non corrette.")
        }
    }
    return (
        <div>
            <Heading level={1}>Purrfect Potty Configurator Login</Heading>
            <p className="text-muted">
                Accessing instance {address}
            </p>
            <Panel>
                <Form>
                    <Form.Row>
                        <Form.Field onSimpleChange={e => setEmail(e)} value={email} required={true}
                                    placeholder={"Email"}>
                        </Form.Field>
                    </Form.Row>
                    <Form.Row>
                        <Form.Field type="password" onSimpleChange={e => setPassword(e)} value={password}
                                    required={true}
                                    placeholder={"Password"} autoComplete={"Password"}>
                        </Form.Field>
                    </Form.Row>
                </Form>
                <Chapter>
                    <Button children={"Login"} onClick={e => login()}></Button>
                </Chapter>
            </Panel>
        </div>
    )
}