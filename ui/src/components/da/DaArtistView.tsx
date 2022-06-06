import { useEffect, useState } from 'react';
import { Space, Image, Card, Badge, Row, Col, Button, notification, Pagination, Divider } from 'antd';
import Cookies from 'universal-cookie';
import { CloudDownloadOutlined, LinkOutlined } from '@ant-design/icons';

const { Meta } = Card;
interface IDaArtistViewProps {
    apiUrl: string
}

interface IGalleryGet {
    ID: number,
    ARTIST_NAME: string,
    NUM_IMAGES: number,
    DIRECTORY_NAME: string,
    FILENAME: string
}

const cookies = new Cookies();

const DaArtistView = (props: IDaArtistViewProps) => {
    const [artistData, setartistData] = useState<IGalleryGet[]>([])
    const [imgSize, setImgSize] = useState<number>(200)
    const [currentDownloadTasks, setCurrentDownloadTasks] = useState<string[]>([])


    const loadArtists = async () => {
        const response = await fetch(`${props.apiUrl}/api/da/artists`);
        const galleries = await response.json();
        setartistData(galleries)
    }

    useEffect(() => {

        loadArtists()

        const cookImgSize = cookies.get("imgSize")
        if (typeof cookImgSize === "string") {
            const cookImgNumSize = Number(cookImgSize)
            if (cookImgNumSize >= 100 && cookImgNumSize <= 500)
                setImgSize(cookImgNumSize)

        }

    }, []);

    const onDownloadClick = (event: any, galleryId: number) => {

        const isArchiveReady = (task_id: string) => {
            fetch(`${props.apiUrl}/api/tasks/darchive/${task_id}`, {
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
                    setCurrentDownloadTasks([])
                    notification.open({
                        key: currentDownloadTasks[0],
                        message: 'Download Ready!',
                        description: `${props.apiUrl}/${data["result"]}`,
                        duration: 5
                    });
                    window.location.href = `${props.apiUrl}/${data["result"]}`

                    clearInterval(interval)
                })
                .catch((error) => {
                    console.error('Error:', error);
                });

        }


        let interval: number = 0;
        const submitArchiveRequest = async (artistid: number) => {
            if (typeof artistid === "undefined") {
                return null
            }
            fetch(`${props.apiUrl}/api/tasks/darchive`, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    'artistID': artistid
                })
            })
                .then(response => response.json())
                .then(data => {
                    setCurrentDownloadTasks([...currentDownloadTasks, data["data"]["task_id"]])
                    notification.open({
                        key: currentDownloadTasks[0],
                        message: 'Download Requested',
                        description: `DownloadID: ${data["data"]["task_id"]}`,
                        duration: 2
                    });
                    interval = setInterval(isArchiveReady, 2000, data["data"]["task_id"]);
                })
                .catch((error) => {
                    console.error('Error:', error);
                });
        }
        submitArchiveRequest(galleryId);
    }

    const generateGalleryCard = (gallData: IGalleryGet) => {
        return (

            <Card
                style={{ width: imgSize, height: imgSize + 100 }}
                cover={
                    generateGalleryImage(gallData)
                }
            >
                <Button
                    onClick={e => onDownloadClick(e, gallData.ID)}
                    style={{ position: "absolute", bottom: 0, right: 0, margin: "10px" }}
                    type="primary"
                    icon={<CloudDownloadOutlined />}
                    shape="round"
                    size="small" />

                <a href={`${props.apiUrl}/grid/da/artist/${gallData.ID}`}>
                    <Meta style={{ position: "relative", bottom: 0, left: 0, margin: "10px" }}
                        title={`${gallData.ARTIST_NAME}`}
                        description={`${gallData.NUM_IMAGES} Image${gallData.NUM_IMAGES == 1 ? '' : 's'}`}
                    />
                </a>
            </Card>
        )
    }


    const generateGalleryImage = (gallData: IGalleryGet) => {
        return (
            <Image
                width="100%"
                height={imgSize}
                src={`${props.apiUrl}/da/${gallData.DIRECTORY_NAME}/${gallData.FILENAME}.webp`}
                fallback="data:image/png;base64,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"
            />

        )
    }


    return (
        <>
            <Row>
                <Col span={24}>
                    <Space size={[8, 16]} wrap>
                        {artistData.map((artist) => generateGalleryCard(artist))}
                        {artistData.length == 0 ? "Nothing Here...." : ""}
                    </Space>
                </Col>
            </Row>
        </>
    )


}


export default DaArtistView;