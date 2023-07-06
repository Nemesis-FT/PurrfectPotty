import React, {useEffect} from 'react';
import Style from "./Landing.module.css";
import {Heading, Panel,} from "@steffo/bluelib-react";
import {useAppContext} from "../Context";
import {useNavigate} from "react-router-dom";

export default function Landing() {
    const {address, setAddress} = useAppContext()
    const navigator = useNavigate()

    useEffect(() => {

        if (localStorage.getItem("address") && address == null) {
            let address = localStorage.getItem("address")
            setAddress(address)
            navigator("/login")
        }
    })

    return (
        <div className={Style.Landing}>
            <div className={Style.lander} style={{minWidth: "unset"}}>
                <Heading level={1}>Purrfect Potty Configurator</Heading>
                <p className="text-muted">
                    The reactive frontend that allows configuration of your Purrfect Potty device.
                </p>

            </div>
            <Panel style={{minWidth: "unset"}}>
                To access the configuration panel of your device, please add the ip address of the data proxy after the
                base address of this page (after a "/"). You will be redirected to the appropriate login page.
            </Panel>
        </div>
    );
}