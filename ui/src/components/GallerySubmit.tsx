import React, { useState, useEffect, useRef } from 'react';
import { Form, Input, Button, message, InputRef, notification } from 'antd';

interface IGallerySubmitProps {
    apiUrl: string
}

const success = (str: string) => {
    message.success(str);
};

const error = (str: string) => {
    message.error(str);
};

const GallerySubmit = (props: IGallerySubmitProps) => {
    const urlInput = useRef<InputRef>(null);



    const onFinish = (values: any) => {

        const isDownloadReady = (task_id: string) => {
            fetch(`${props.apiUrl}/api/tasks/gallery/${task_id}`, {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                }
            })
                .then(response => response.json())
                .then(data => {
                    if (data['status'] !== 'SUCCESS')
                        return
                    notification.open({
                        key: task_id,
                        message: 'Gallery Added!',
                        description: `${data['result'][0]} Galleries Added, ${data["result"][1]} Images Added`,
                        duration: 5
                    });

                    clearInterval(interval)
                })
                .catch((error) => {
                    console.error('Error:', error);
                });

        }


        let interval: number = 0;
        const submitValues = async (values: any) => {
            if (typeof values["Gallery URL"] === "undefined") {
                return null
            }
            fetch(`${props.apiUrl}/api/tasks/gallery`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    gallery_url: values["Gallery URL"]
                })
            })
                .then(response => response.json())
                .then((data) => {
                    if (typeof data["task_id"] === "undefined" || typeof data["status"] === "undefined") {
                        notification.open({
                            key: values["Gallery URL"],
                            message: 'FAILED TO SUBMIT',
                            description: `FAILED TO SUBMIT`,
                            duration: 0
                        });
                        return
                    }
                    notification.open({
                        key: values["Gallery URL"],
                        message: 'Gallery Queued for download',
                        description: `task id: ${data["task_id"]}`,
                        duration: 2
                    });
                    interval = setInterval(isDownloadReady, 2500, data["task_id"]);
                })
        }
        submitValues(values)
    };

    useEffect(() => {
        if (urlInput.current) {
            urlInput.current.focus();
        }
    }, [urlInput]);


    return (
        <>

            <Form
                name="basic"
                labelCol={{ span: 4 }}
                wrapperCol={{ span: 16 }}
                initialValues={{ remember: true }}
                onFinish={onFinish}
                autoComplete="off"
            >
                <Form.Item
                    label="Gallery URL"
                    name="Gallery URL"
                    rules={[
                        {
                            required: true
                        },
                        {
                            required: true,
                            whitespace: true,
                            message: "Invalid URL",
                            type: 'url'
                        }
                    ]}
                >
                    <Input size="large" ref={urlInput} />
                </Form.Item>
                <Form.Item wrapperCol={{ offset: 4, span: 16 }}>
                    <Button type="primary" htmlType="submit" size="large" block>
                        Submit
                    </Button>
                </Form.Item>
            </Form>

        </>

    );
};

export default GallerySubmit;